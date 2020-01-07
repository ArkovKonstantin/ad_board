import aiopg.sa
from datetime import datetime as dt
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date,
    DateTime)

meta = MetaData()
posts = Table(
    'posts', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(200)),
    Column('description', String(1000)),
    Column('price', Integer)
    # TODO column image list
    # Column('image', String), не больше 3 ех фото
)


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


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
