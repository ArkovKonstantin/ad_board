from aiohttp import web
from api.settings import config
from api.routes import setup_routes
from api.db import init_pg, close_pg, init_redis, close_redis
from api.middlewares import process_req_param
import logging


def init_app():
    app = web.Application(middlewares=[process_req_param])
    logging.basicConfig(level=logging.DEBUG)
    setup_routes(app)
    app['config'] = config
    app.on_startup.extend([init_pg, init_redis])
    app.on_cleanup.extend([close_pg, close_redis])
    return app


if __name__ == '__main__':
    app = init_app()
    web.run_app(app, port=8001)
