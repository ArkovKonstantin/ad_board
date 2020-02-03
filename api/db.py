import time
from functools import wraps

import aiopg.sa
from datetime import datetime as dt
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date,
    DateTime, ARRAY, Text)
import aioredis
from sqlalchemy.exc import OperationalError
import asyncio

meta = MetaData()
posts = Table(
    'posts', meta,

    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(200)),
    Column('description', String(1000)),
    Column('price', Integer),
    Column('images', ARRAY(String(200))),
    Column('pub_date', DateTime, index=True, default=dt.utcnow())
)


def retry_conn(retries=3, timeout=5):
    def decor(cor):
        @wraps(cor)
        async def wrapper(app):
            count = 0
            while count < retries:
                try:
                    return await cor(app)
                except:
                    count += 1
                    await asyncio.sleep(timeout)

        return wrapper

    return decor


@retry_conn()
async def init_pg(app):
    conf = app['config']['postgres']

    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


@retry_conn()
async def init_redis(app):
    conf = app['config']['redis']

    redis = await aioredis.create_redis_pool((
        conf['host'], conf['port']
    ))
    app['redis'] = redis


async def close_redis(app):
    app['redis'].close()
    await app['redis'].wait_closed()


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
