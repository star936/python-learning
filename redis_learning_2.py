# coding: utf-8

import time

import redis

from redis_learning import acquire_lock_with_timeout, release_lock


pool = redis.ConnectionPool(host='localhost', port=6379)
conn = redis.Redis(connection_pool=pool)


def string_to_score(string, ignore_case=False):
    """字符串转换成数字分值:基于数据的前6个字节(48位二进制)进行转换"""
    if ignore_case:
        string = string.lower()
    pieces = list(map(ord, string[:6]))
    while len(pieces) < 6:
        pieces.append(-1)

    score = 0
    for p in pieces:
        # 给每一个ASCII值加上1，使得0作为空字符的填充值
        score = score * 257 + p + 1
    # 加上len(string) > 6标示字符串长度是否超过6个字符
    return score * 2 + (len(string) > 6)


def create_user(connection, login, name):
    """创建新的用户信息的散列"""
    llogin = login.lower()
    lock = acquire_lock_with_timeout(connection, 'user:' + llogin, 1)
    if not lock:
        return None

    if connection.hget('users:', llogin):    # 使用一个散列存储了用户名(小写)与用户ID的映射
        release_lock(connection, 'user:' + llogin, lock)
        return None
    # 用户ID
    uid = connection.incr('user:id:')
    pipe = connection.pipeline(True)
    pipe.hset('users:', llogin, uid)
    pipe.hmset('user:%s' % uid, {
        'login': login,
        'name': name,
        'id': uid,
        'followers': 0,
        'following': 0,
        'posts': 0,
        'signup': time.time()
    })
    pipe.execute()
    release_lock(connection, 'user:' + llogin, lock)
    return uid


def create_status(connection, uid, message, **data):
    """创建状态消息散列"""
    pipe = connection.pipeline(True)
    pipe.hget('user:' + uid, 'login')
    pipe.incr('status:id:')
    login, sid = pipe.execute()
    # 发布状态消息前先验证用户账号是否存在
    if not login:
        return None
    data.update({
        'message': message,
        'posted': time.time(),
        'id': sid,
        'uid': uid,
        'login': login
    })
    pipe.hmset('status:%s' % sid, data)
    # 更新用户已发消息状态数量
    pipe.hincrby('user:%s' % uid, 'posts')
    pipe.execute()

    return sid


def get_status_messages(connection, uid, timeline='home:', page=1, count=30):
    """默认从主页从时间线获取给定页数的最新状态消息，另外还可以获取个人时间线"""
    # 获取时间线上最新的状态消息ID
    statuses = connection.zrevrange('%s%s' % (timeline, uid), (page-1) * count, page * count -1)
    pipe = connection.pipeline(True)
    for sid in statuses:
        pipe.hgetall('status:%s' % sid)
    return filter(None, pipe.execute())


HOME_TIMELINE_SIZE = 1000


def follower_user(connection, uid, other_uid):
    """对执行关注操作的用户的主页时间线进行更新"""
    fkey1 = 'following:%s' % uid
    fkey2 = 'followers:%s' % other_uid

    if connection.zscore(fkey1, other_uid):    # 如果uid指定的用户已经关注了other_uid指定的用户，则不重复关注
        return None
    now = time.time()
    pipe = connection.pipeline(True)
    pipe.zadd(fkey1, other_uid, now)
    pipe.zadd(fkey2, uid, now)

    pipe.zrevrange('profile:%s' % other_uid, 0, HOME_TIMELINE_SIZE - 1, withscores=True)
    following, followers, status_and_socre = pipe.execute()
    # 修改两个用户的散列，更新他们的正在关注数量和关注者数量
    pipe.hincrby('user:%s' % uid, 'following', int(following))
    pipe.hincrby('user:%s' % other_uid, 'followers', int(followers))

    if status_and_socre:
        # 对执行关注操作的用户的主页时间线进行更新
        pipe.zadd('home:%s' % uid, **dict(status_and_socre))
    pipe.zremrangebyrank('home:%s' % uid, 0, -HOME_TIMELINE_SIZE - 1)

    pipe.execute()
    return True


def unfollow_user(connection, uid, other_uid):
    """取消关注某个用户"""
    fkey1 = 'following:%s' % uid
    fkey2 = 'followers:%s' % other_uid

    if not connection.zscore(fkey1, other_uid):    # 如果uid指定的用户已经取消关注了other_uid指定的用户，则不重复取消关注
        return None

    pipe = connection.pipeline(True)
    pipe.zrem(fkey1, other_uid)
    pipe.zrem(fkey2, uid)
    pipe.zrevrange('profile:%s' % other_uid, 0, HOME_TIMELINE_SIZE - 1, withscores=True)
    following, followers, statuses = pipe.execute()[-3:]

    # 修改两个用户的散列，更新他们的正在关注数量和关注者数量
    pipe.hincrby('user:%s' % uid, 'following', int(following))
    pipe.hincrby('user:%s' % other_uid, 'followers', int(followers))
    if statuses:
        # 对执行取消关注操作的用户的主页时间线进行更新
        pipe.zrem('home:%s' % uid, *statuses)

    pipe.execute()
    return True

