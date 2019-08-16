# coding: utf-8

import fcntl
from functools import partial


def chunked_file_reader(file, block_size=1024 * 8):
    """生成器函数: 分块读取文件内容,使用iter函数"""
    for chunk in iter(partial(file.read, block_size), ''):
        yield chunk


class Lock:
    def __init__(self, filename, block=True):
        """block 参数为 true代表阻塞式获取。  False为非阻塞，如果获取不到立刻返回 false"""
        self.filename = filename
        self.block = block
        self.handle = open(filename, 'w')

    def acquire(self):
        if not self.block:
            try:
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except:
                return False
        else:
            fcntl.flock(self.handle, fcntl.LOCK_EX)
            return True

    def release(self):
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.handle.close()
