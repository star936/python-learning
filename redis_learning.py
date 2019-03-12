# coding: utf-8

import datetime
import math
import time
import uuid

import redis


pool = redis.ConnectionPool(host='localhost', port=6379)
conn = redis.Redis(connection_pool=pool)


# 1. 分布式锁
def acquire_lock(connection, lock_name, acquire_timeout=10):
    """使用setnx命令获取锁,支持获取锁失败在一定时间内重试"""
    identifier = str(uuid.uuid4())

    end = time.time() + acquire_timeout
    while time.time() < end:
        if connection.setnx('lock:' + lock_name, identifier):
            return identifier
        time.sleep(.001)
    return False


def acquire_lock_with_timeout(connection, lock_name, acquire_timeout=10, lock_timeout=10):
    """获取锁, 支持锁超时"""
    identifier = str(uuid.uuid4())
    lock_name = 'lock:' + lock_name
    lock_timeout = int(math.ceil(lock_timeout))

    end = time.time() + acquire_timeout
    while time.time() < end:
        if connection.set(lock_name, identifier, datetime.timedelta(seconds=lock_timeout)):
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
    pipe.zremrangebyscore(sem_name, '-inf', now - timeout)  # 清除过期的信号持有者
    pipe.zadd(sem_name, identifier, now)  # 尝试获取信号量
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
def acquire_fair_semphore(connection, sem_name, limit, timeout=10):
    identifier = str(uuid.uuid4())
    czset = sem_name + ':owner'
    counter_name = sem_name + ':counter'

    now = time.time()
    pipe = connection.pipeline(True)
    # 删除超时信号量
    pipe.zremrangebyscore(sem_name, '-inf', now - timeout)  # 清除过期的信号持有者
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



