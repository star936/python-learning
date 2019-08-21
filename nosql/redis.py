# coding: utf-8

import datetime
import json
import math
import re
import redis
import time
import uuid

pool = redis.ConnectionPool(host='localhost', port=6379)
conn = redis.Redis(connection_pool=pool)


# 1. 分布式锁
def acquire_lock(connection, lock_name, acquire_timeout=10.0):
    """使用setnx命令获取锁,支持获取锁失败在一定时间内重试"""
    identifier = str(uuid.uuid4())

    end = time.time() + acquire_timeout
    while time.time() < end:
        if connection.setnx('lock:' + lock_name, identifier):
            return identifier
        time.sleep(.001)
    return False


def acquire_lock_with_timeout(connection,
                              lock_name,
                              acquire_timeout=10,
                              lock_timeout=10):
    """获取锁, 支持锁超时"""
    identifier = str(uuid.uuid4())
    lock_name = 'lock:' + lock_name
    lock_timeout = int(math.ceil(lock_timeout))

    end = time.time() + acquire_timeout
    while time.time() < end:
        if connection.set(lock_name, identifier,
                          datetime.timedelta(seconds=lock_timeout)):
            # connection.expire(lock_name, lock_timeout)
            return identifier
        elif not connection.ttl(lock_name):
            connection.expire(lock_name, lock_timeout)
        time.sleep(.001)

    return False


def release_lock(connection, lock_name, identifier):
    """释放锁"""
    pipe = connection.pipeline(True)
    lock_name = 'lock:' + lock_name

    while True:
        try:
            pipe.watch(lock_name)
            if pipe.get(lock_name) == identifier:
                pipe.multi()
                pipe.delete(lock_name)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except redis.exceptions.WatchError:
            pass
    return False


# 2. 计数信号量: 限制一项资源最多能够被多少进程访问.
def acquire_semaphore(connection, sem_name, limit, timeout=10):
    """获取信号量"""
    identifier = str(uuid.uuid4())
    now = time.time()

    pipe = connection.pipeline(True)
    pipe.zremrangebyscore(sem_name, '-inf', now - timeout)    # 清除过期的信号持有者
    pipe.zadd(sem_name, identifier, now)    # 尝试获取信号量
    # 检查是否成功获取了信号
    pipe.zrank(sem_name, identifier)
    if pipe.execute()[-1] < limit:
        return identifier

    # 信号量获取失败，删除之前  添加的标示符
    connection.zrem(sem_name, identifier)
    return None


def release_semaphore(connection, sem_name, identifier):
    """释放信号量: 如果信号量被正确释放则返回True; 返回False表示信号量已经因为过期而被删除了"""
    return connection.zrem(sem_name, identifier)


"""
上述分布式锁和计数信号量都存在一些问题:
   在多主机环境下，每当锁或信号量因为系统时钟的细微不同而导致锁的获取结果出现剧烈变化时，则这个锁或信号量是不公平的.
不公平的锁或信号量可能会造成客户端永远也无法取得它原本应该得到的锁或信号量.
解决方法:
   给信号量实现添加一个计数器和一个有序集合。其中计数器通过持续自增操作，创建出一种类似于计时器的机制，
确保最先对计时器进行自增操作的客户端能够获取到信号量;通过检查客户端生成的标识符在有序集合中的排名来判断客户端是否取得了信号量.
"""


# 3. 公平信号量
def acquire_fair_semaphore(connection, sem_name, limit, timeout=10):
    """获取公平信号量: 维护了2个有序集合(超时有序集合及信号拥有者有序集合)和一个计时器"""
    identifier = str(uuid.uuid4())
    czset = sem_name + ':owner'
    counter_name = sem_name + ':counter'

    now = time.time()
    pipe = connection.pipeline(True)
    # 删除超时信号量
    pipe.zremrangebyscore(sem_name, '-inf', now - timeout)    # 清除过期的信号持有者
    pipe.zinterstore(czset, {czset: 1, counter_name: 0})

    # 对计数器执行自增操作，并获取自增之后的值
    pipe.incr(counter_name)
    counter = pipe.execute()[-1]

    pipe.zadd(sem_name, identifier, now)
    pipe.zadd(czset, identifier, counter)
    # 通过检查排名判断客户端是否获取了信号量
    pipe.zrank(czset, identifier)
    if pipe.execute()[:-1] < limit:
        return identifier

    pipe.zrem(sem_name, identifier)
    pipe.zrem(czset, identifier)
    pipe.execute()
    return None


def release_fair_semaphore(connection, sem_name, identifier):
    """释放公平信号量: 如果信号量被正确释放则返回True; 返回False表示信号量已经因为过期而被删除了"""
    pipe = connection.pipeline(True)
    pipe.zrem(sem_name, identifier)
    pipe.zrem(sem_name + ':owner', identifier)
    return pipe.execute()[0]


def refresh_fair_semaphore(connection, sem_name, identifier):
    """更新公平信号量: 如果信号量已经存在则刷新其超时时间;如果信号量已经因为超时而被删除则释放信号量"""
    if connection.zadd(sem_name, identifier, time.time()):
        refresh_fair_semaphore(connection, sem_name, identifier)
        return False
    return True


"""上面的信号量(不公平及公平信号量)都还存在一个问题----竞争问题：
   当两个进程A和B都尝试获取剩余的一个信号量时，即使A首先对计数器进行了自增操作，但是只要B能够抢先将自己的标识符添加到
   有序集合里并检查标识符在有序集合中的排名，那么B就可以获取到信号量；之后当A也将自己的标识符放到有序集合并检查
   标识符在集合中的排名时，A将偷走B获取的信号量，而B只有在释放或刷新信号量时才能觉察到.
"""


def acquire_semaphore_with_lock(connection, sem_name, limit, timeout=10):
    """获取信号量首先获取一个带有短暂超时时间的锁."""
    identifier = acquire_lock(connection, sem_name, acquire_timeout=.01)
    if identifier:
        try:
            return acquire_fair_semaphore(connection, sem_name, limit, timeout)
        finally:
            release_lock(connection, sem_name, identifier)


"""
以聊天为背景，实现具有多个接受者的消息传递
    群组有序集合记录参加群组的用户，其中有序集合的成员为用户的名字，成员分值则是用户在群组内接收到的最大消息ID;
    用户有序集合记录用户参加的群组，其中有序集合的成员为群组ID，成员分值则是用户在群组内接收到的最大消息ID;
    消息有序集合记录群组内发送的消息，其中有序集合的成员为消息体，成员分值则是消息ID.
"""


def send_message(connection, chat_id, sender, message):
    """发送消息"""
    identifier = acquire_lock(connection, 'chat:' + chat_id)
    if not identifier:
        raise Exception("Couldn't get the lock")

    try:
        # 生成新消息ID
        mid = connection.incr('ids:' + chat_id)
        ts = time.time()
        packed = {'id': mid, 'sender': sender, 'ts': ts, 'message': message}
        connection.zadd('msgs:' + chat_id, packed, mid)
    finally:
        release_lock(connection, 'chat:' + chat_id, identifier)


def create_chat(connection, sender, recipients, message, chat_id=None):
    """创建群组"""
    # 获取一个新的chat ID
    chat_id = chat_id or str(connection.incr('ids:chat:'))
    recipients.append(sender)
    recipientsd = dict((rec, 0) for rec in recipients)
    pipe = connection.pipeline(True)
    # 将所有参与群组的用户添加到有序集合
    pipe.zadd('chat:' + chat_id, **recipientsd)
    for r in recipients:
        # 初始化已读有序集合
        pipe.zadd('seen:' + r, chat_id, 0)
    pipe.execute()
    return send_message(connection, chat_id, sender, message)


def fetch_message(connection, recipient):
    seen = connection.zrange('seen:' + recipient, 0, -1, withscores=True)
    pipe = connection.pipeline(True)
    # 获取用户每个群组的所有未读消息
    for chat_id, seen_id in seen:
        pipe.zrankbyscore('msgs:' + chat_id, seen_id + 1, 'inf')
    chat_info = list(zip(seen, pipe.execute()))

    for i, ((chat_id, seen_id), messages) in enumerate(chat_info):
        if not messages:
            continue
        messages[:] = map(json.loads, messages)
        # 使用收到的最新消息更新群组有序集合
        seen_id = messages[-1]['id']
        # 更新用户已读消息集合
        connection.zadd('chat:' + chat_id, recipient, seen_id)

        min_id = connection.zrange('chat:' + chat_id, 0, 0, withscores=True)
        pipe.zadd('seen:' + recipient, chat_id, seen_id)

        if min_id:
            # 清除所有人都阅读过的消息
            pipe.zremrangebyscore('msgs:' + chat_id, 0, min_id[0][1])
        chat_info[i] = (chat_id, messages)

    pipe.execute()

    return chat_info


def join_chat(connection, chat_id, user):
    """加入群组"""
    mid = int(connection.get('ids:' + chat_id))

    pipe = connection.pipeline(True)
    pipe.zadd('chat:' + chat_id, user, mid)
    pipe.zadd('seen:' + user, chat_id, mid)
    pipe.execute()


def left_chat(connection, chat_id, user):
    """离开群组"""
    pipe = connection.pipeline(True)
    # 将用户从群组表删除并删除其用户表
    pipe.zrem('chat:' + chat_id, user)
    pipe.zrem('seen:' + user, chat_id)
    # 获取群组用户量
    pipe.zcard('chat:' + chat_id)

    if not pipe.execute()[-1]:    # 如果已经没有别的用户
        pipe.delete('msgs:' + chat_id)
        pipe.delete('ids:' + chat_id)
        pipe.execute()
    else:
        # 找出群组中被所有人都阅读过的消息,并删除
        seen = connection.zrange('chat:' + chat_id, 0, 0, withscores=True)
        connection.zremrangebyscore('chat:' + chat_id, 0, seen[0][1])


"""
基于redis的搜索
"""

STOP_WORDS = set('''able about across after all almost also am among
an and any are as at be because been but by can cannot could dear did
do does either else ever every for from get got had has have he her
hers him his how however if in into is it its just least let like
likely may me might most must my neither no nor not of off often on
only or other our own rather said say says she should since so some
than that the their them then there these they this tis to too twas us
wants was we were what when where which while who whom why will with
would yet you your'''.split())

WORD_RE = re.compile("[a-z']{2,}")
QUERY_RE = re.compile("[+-]?[a-z']{2,}")


def tokenize(content):
    """对文本内容进行标标记化处理"""
    words = set()

    for match in WORD_RE.finditer(content.lower()):
        word = match.group().strip("'")
        if len(word) > 2:
            words.add(word)
    return words - STOP_WORDS


def index_document(connection, doc_id, content):
    """对document建立反向索引"""
    words = tokenize(content)

    pipe = connection.pipeline(True)
    for word in words:
        pipe.sadd('idx:' + word, doc_id)
    return len(pipe.execute())


def _set_common(connection, method, names, ttl=30, execute=True):
    """一个执行交集、并集、差集的辅助函数"""
    idx = str(uuid.uuid4())

    pipe = connection.pipeline(True) if execute else connection
    names = ['idx:' + name for name in names]
    # 为将要进行的集合操作设置相应的参数
    getattr(pipe, method)('idx:' + idx, *names)
    pipe.expire('idx:' + idx, ttl)
    if execute:
        pipe.execute()
    return idx


def intersect(connection, items, ttl=30, execute=True):
    """并集计算"""
    return _set_common(connection, 'sinterstore', items, ttl, execute)


def union(connection, items, ttl=30, execute=True):
    """交集计算"""
    return _set_common(connection, 'sunionstore', items, ttl, execute)


def difference(connection, items, ttl=30, execute=True):
    """差集计算"""
    return _set_common(connection, 'sdiffstore', items, ttl, execute)


def parse(query):
    """对搜索语句进行语法分析"""
    # 存储不需要的单词
    unwanted = set()
    # 存储需要进行交集计算的单词
    all = []
    # 存储目前以发现的同义词
    current = set()

    for match in QUERY_RE.finditer(query.lower()):
        word = match.group()
        prefix = word[:1]
        if prefix in '+-':
            word = word[1:]
        else:
            prefix = None
        word = word.strip("'")
        if len(word) < 2 or word in STOP_WORDS:
            continue
        if prefix == '-':
            unwanted.add(word)
            continue

        if current and not prefix:
            # 如果在同义词集合不为空且遇到无+号前缀的单词时创建一个新的同义词集合
            all.append(list(current))
            current = set()
        current.add(word)
    if current:
        all.append(list(current))
    return all, list(unwanted)


def parse_and_search(connection, query, ttl=30):
    """分析查询语句并搜索文档"""
    all, unwanted = parse(query)
    if not all:
        return None
    to_intersect = []
    for w in all:
        if len(w) > 1:
            # 如果同义词列表包含的单词不止一个则执行并集计算
            to_intersect.append(union(connection, w, ttl))
        else:
            # 如果同义词列表只包含一个单词则使用改单词
            to_intersect.append(w[0])
    if len(to_intersect) > 1:
        # 如果并集计算结果不止一个则执行交集计算
        intersect_result = intersect(connection, to_intersect, ttl)
    else:
        # 如果并集计算结果只有一个则它就是交集计算结果
        intersect_result = to_intersect[0]
    if unwanted:
        # 如果指定了不需要的单词则从交集计算结果中移除包含这些单词的文档
        unwanted.insert(0, intersect_result)
        return difference(connection, unwanted, ttl)
    return intersect_result


def search_and_sort(connection,
                    query,
                    id=None,
                    ttl=300,
                    sort='-updated',
                    start=0,
                    num=20):
    """分析查询语句然后进行搜索，并对搜索结果进行排序"""
    # 决定按照文档的哪个属性进行排序以及是升序还是倒序
    desc = sort.startswith('-')
    sort = sort.lstrip('-')
    by = 'kb:doc:*->' + sort
    # 排序是以数值形式还是字母形式
    alpha = sort not in ('updated', 'id', 'created')
    # 如果用户给定了搜索结果并且这个结果仍然存在，则延长过期时间
    if id and not connection.expire(id, ttl):
        id = None
    # 如果没有给定已有的搜索结果则执行一次搜索
    if not id:
        id = parse_and_search(connection, query, ttl)

    pipe = connection.pipeline(True)
    # 获取结果集合的数量
    pipe.scard('idx:' + id)
    # 根据指定属性对结果进行排序
    pipe.sort('idx:' + id, by=by, alpha=alpha, desc=desc, start=start, num=num)
    results = pipe.execute()
    # 返回搜索结果包含的元素数量，搜索结果本身以及搜索结果的id
    return results[0], results[1], id


"""使用有序集合对搜索结果进行排序"""


def search_and_zsort(connection,
                     query,
                     id=None,
                     ttl=300,
                     update=1,
                     vote=0,
                     start=0,
                     num=20,
                     desc=True):
    """更新之后的函数可以进行搜索并同时基于投票数量和更新时间进行排序"""
    # 刷新已有搜索结果的生存时间
    if id and not connection.expire(id, ttl):
        id = None
    if not id:
        id = parse_and_search(connection, query, ttl=ttl)
        search_socres = {id: 0, 'sort:update': update, 'sort:vote': vote}
        id = zintersect(connection, search_socres, ttl)
    pipe = connection.pipeline(True)
    pipe.zcard('idx:' + id)
    if desc:
        pipe.zrevrange('idx:' + id, start, start + num - 1)
    else:
        pipe.zrange('idx:' + id, start, start + num - 1)
    result = pipe.execute()
    return result[0], result[1], id


def _zset_common(connection, method, scores, ttl=30, **kwargs):
    id = str(uuid.uuid4())
    execute = kwargs.pop('_execute', True)
    pipe = connection.pipeline(True) if execute else connection
    for key in scores.keys():
        scores['idx:' + key] = scores.pop(key)
    getattr(pipe, method)('idx:' + id, scores, **kwargs)
    pipe.expire('idx:' + id, ttl)
    if execute:
        return pipe.execute()
    return id


def zintersect(connection, items, ttl=30, **kwargs):
    return _zset_common(connection, 'zinterstore', dict(items), ttl, **kwargs)


def zunion(connection, items, ttl=30, **kwargs):
    return _zset_common(connection, 'zunionstore', dict(items), ttl, **kwargs)
