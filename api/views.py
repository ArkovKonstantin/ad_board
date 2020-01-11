import json

from aiohttp import web
import db
import math
from sqlalchemy import desc, asc
from schema import schema
from jsonschema import Draft3Validator, FormatChecker


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


async def post_list(request):
    response_data = {}
    sql_query = db.posts.select()
    sql_query = filter(request, sql_query)
    sql_query = paginate(request, sql_query, response_data)
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(sql_query)
        records = await cursor.fetchall()
        # response_data['results'] = [dict(p) for p in records]
    return web.json_response(response_data)


async def create_post(request):
    # form = request.post()
    data = await request.json()
    print('DATA')
    print(data)

    v = Draft3Validator(schema, format_checker=FormatChecker())
    if v.is_valid(data):
        print('data is valid')
        print()
        print(db.posts.insert().values(**data))
        async with request.app['db'].acquire() as conn:
            cursor = await conn.execute(db.posts.insert().values(**data))
            post_id = await cursor.fetchone()
        return web.HTTPCreated(body=json.dumps({'id': post_id[0]}),
                               content_type='application/json')
    else:
        print('data not valid')
        print()
        # print(list((type(err.path), err.path.pop())
        #            for err in v.iter_errors(data)))
        response_data = {'errors': dict((err.path.pop(), err.message)
                                        for err in v.iter_errors(data))}
        return web.HTTPBadRequest(body=json.dumps(response_data),
                                  content_type='application/json')
