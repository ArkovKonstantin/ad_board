from aiohttp import web

from settings import config
from routes import setup_routes
from db import init_pg, close_pg, init_redis, close_redis

app = web.Application()
setup_routes(app)
app['config'] = config
app.on_startup.extend([init_pg, init_redis])
app.on_cleanup.extend([close_pg, close_redis])
web.run_app(app, port=8001)
