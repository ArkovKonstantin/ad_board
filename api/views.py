from aiohttp import web
import db


async def handle(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.posts.select())
        records = await cursor.fetchall()
        posts = [dict(p) for p in records]
    return web.json_response(posts)
