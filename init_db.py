import time

from sqlalchemy import create_engine, MetaData

from api.settings import config
from api.db import posts
from sqlalchemy.exc import OperationalError

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[posts])


def sample_data(engine):
    conn = engine.connect()

    conn.execute(posts.insert(), [
        {'name': 'camera', 'description': 'sony', 'price': 1000, 'images':
            ['image1', 'image2', 'image3']},
        {'name': 'phone', 'description': 'nokia3310', 'price': 500, 'images':
            ['image4', 'image5', 'image6']},
        {'name': 'auto', 'description': 'lada', 'price': 2000, 'images':
            ['image7', 'image8', 'image9']}
    ])
    conn.close()


def init_db():
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)
    retries = 3
    timeout = 5
    while retries > 0:
        try:
            create_tables(engine)
            sample_data(engine)
            return
        except OperationalError:
            retries -= 1
            time.sleep(timeout)


if __name__ == '__main__':
    init_db()
