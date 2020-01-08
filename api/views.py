from aiohttp import web
import db
import math
from sqlalchemy import desc, asc


# limit offset approach
def paginate(request, sql_query, response_data, limit=10):
    page = int(request.query.get('page', 1))
    limit = int(request.query.get('limit', limit))
    offset = (page - 1) * limit
    response_data['next'] = f'{request.url}?page={page + 1}&limit={limit}'
    if page > 1:
        response_data['prev'] = f'{request.url}?page={page - 1}&limit={limit}'
    return sql_query.limit(limit).offset(offset)


# /api/v1/posts?filter[col]=(asc|desc)
def filter(request, sql_query):
    args = []
    for key in request.query:
        if key.startswith('filter'):
            _, col = key[:-1].split('[')
            if request.query[key] == 'desc':
                args.append(desc(col))
            elif request.query[key] == 'asc':
                args.append(asc(col))

    return sql_query.order_by(*args)


async def handle(request):
    response_data = {}
    sql_query = db.posts.select()
    sql_query = filter(request, sql_query)
    sql_query = paginate(request, sql_query, response_data)
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(sql_query)
        records = await cursor.fetchall()
        response_data['results'] = [dict(p) for p in records]
    return web.json_response(response_data)
