from sqlalchemy import create_engine, MetaData

from api.settings import config
from api.db import posts

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[posts])


def sample_data(engine):
    conn = engine.connect()

    conn.execute(posts.insert(), [
        {'name': 'camera', 'description': 'sony', 'price': 1000},
        {'name': 'phone', 'description': 'nokia3310', 'price': 500},
        {'name': 'auto', 'description': 'lada', 'price': 2000},
    ])
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
