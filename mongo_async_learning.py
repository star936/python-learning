# coding: utf-8

from contextlib import closing
import asyncio
import datetime
import time

from motor.motor_asyncio import AsyncIOMotorClient


client = AsyncIOMotorClient(host='localhost', port=15461, username='root', password='root',
                            authSource='test', authMechanism='SCRAM-SHA-1')

db = client['test']
places = db['User']
st = datetime.datetime(2018, 11, 6, 9, 30, 0)


async def update_time(data):
    """删除mongodb document中某字段"""
    await places.update_one({'_id': data['_id']}, {'$unset': {'_class': ''}})
    print(data['_id'])


async def main():
    cur = places.find({'_class': {'$exists': True}}).sort('_id', 1).limit(1000)
    results = []
    async for c in cur:
        results.append(update_time(c))
    await asyncio.gather(*results)


if __name__ == '__main__':
    now = time.time()
    try:
        with closing(asyncio.get_event_loop()) as loop:
            loop.run_until_complete(main())
    except Exception as e:
        print(e)
    print('time is %d' % (time.time()-now))
