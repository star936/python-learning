# coding: utf-8

import pandas as pd
import sqlite3
import psycopg2

HOST = 'localhost'
PORT = 5432
DATABASE = 'test'
USER = 'root'
PASSWORD = 'root'

pg_conn = psycopg2.connect(host=HOST,
                           port=PORT,
                           user=USER,
                           password=PASSWORD,
                           dbname=DATABASE)
pg_cur = pg_conn.cursor()

pg_sql = "INSERT INTO city(id, country, state, city, zip, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s)"

conn = sqlite3.connect('City.sqlite')

cursor = conn.cursor()


def executemany(cur):
    values = cur.fetchall()
    data = []
    num = 0
    for v in values:
        data.append([v[0], v[1], v[2], v[3], v[4], v[5], v[6]])
        if len(data) == 500:
            num += 1
            print(num)
            print(data)
            pg_cur.executemany(pg_sql, data)
            pg_conn.commit()
            data = []

    if len(data) > 0:
        pg_cur.executemany(pg_sql, data)
        pg_conn.commit()

    cur.executemany(pg_sql, data)


def copy_from(cur, filename):
    values = cur.fetchall()
    df = pd.DataFrame(values, columns=['id', 'country', 'state', 'city',
                                       'zip', 'latitude', 'longitude'])
    df.to_csv(filename, index=False)

    with open(filename, 'r') as f:
        next(f)   # 跳过header
        cur.copy_from(f, 'city', sep=',')


if __name__ == '__main__':
    cursor.execute("SELECT * FROM city")
    # 第一种方法
    # executemany(cursor)

    # 第二种方法
    copy_from(cursor, 'city.csv')
    conn.close()
    pg_conn.commit()
    pg_conn.close()

