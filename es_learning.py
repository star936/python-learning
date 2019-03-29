# coding: utf-8

from datetime import datetime, timedelta

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q


CLIENT = Elasticsearch(hosts=['localhost:9200'])
INDEX = 'products'
DOC_TYPE = 'product'


'''
{"query":{"bool":{"filter":[{"term":{"equipment":"flatbed"}},{"term":{"pickup.state":"CA"}},{"range":{"pickup.date":
{"lt":"2019-04-01 00:00:00","gte":"2019-03-25 00:00:00"}}}]}},"aggs":{"days":{"filter":{"range":{"pickup.date":
{"gte":"2019-04-01T00:00:00Z","lt":"2019-03-25T00:00:00Z"}}},"aggs":{"total_distance":{"sum":{"field":"distance"}},
"total_price":{"sum":{"field":"price"}},"data":{"date_histogram":{"field":"pickup.date","interval":"day"},
"aggs":{"day_distance":{"sum":{"field":"distance"}},"day_price":{"sum":{"field":"price"}}}}}}}}
'''


def search_and_aggs():
    """根据条件过滤并计算最近7天内distance、price的总和以及每天的总和"""
    end = datetime.now()
    start = end - timedelta(days=7)

    q = Q('bool', filter=[Q('term', equipment='van'),
                          Q('term', pickup__state='BJ'),
                          Q('range', pickup__date={'gte': start, 'lt': end})])

    s = Search(using=CLIENT, index=INDEX, doc_type=DOC_TYPE).query(q)

    sum_distance = A('sum', field='distance')
    sum_price = A('sum', field='price')

    s.aggs.bucket('days', 'range', field='pickup.date', ranges=[{'from': start, 'to': end}])\
        .metric('total_distance', sum_distance)\
        .metric('total_price', sum_price) \
        .bucket('data', 'date_histogram', field='pickup.date', interval='day', extended_bounds={"min": start, "max": end})\
        .metric('day_distance', sum_distance) \
        .metric('day_price', sum_price)

    response = s.execute()
    bucket = response.aggs['days']['buckets'][0]
    total_distance = bucket['total_distance'].value
    total_price = bucket['total_price'].value

    print('total: distance={}, price={}'.format(total_distance, total_price))

    for r in bucket['data']['buckets']:
        day_distance = r['day_distance']
        day_price = r['day_price']
        print('day sum: distance={}, price={}'.format(day_distance, day_price))
