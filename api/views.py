import json
from aiohttp import web
from api import db
from sqlalchemy import desc, asc
from api.schema import schema
from jsonschema import Draft3Validator, FormatChecker


def paginate(request, sql_query, response_data, limit=10):
    """Используем sql запрос limit offset для пагинации"""
    page = int(request.query.get('page', 1))
    limit = int(request.query.get('limit', limit))
    offset = (page - 1) * limit
    response_data['next'] = f'{request.url.scheme}://{request.url.host}' \
                            f'{request.url.path}?page={page + 1}&limit={limit}'
    if page > 1:
        response_data['prev'] = f'{request.url.scheme}://{request.url.host}' \
                                f'{request.url.path}?page={page - 1}&limit={limit}'
    return sql_query.limit(limit).offset(offset)


def filter(request, sql_query):
    """Обработка переданных параметров в get зпросе"""
    args = []
    for key in request.query:
        if key.startswith('filter'):
            _, col = key[:-1].split('[')
            if request.query[key] == 'desc':
                args.append(desc(col))
            elif request.query[key] == 'asc':
                args.append(asc(col))

    return sql_query.order_by(*args)


def redis_cache(cor):
    """Сохраненяем GET запрос в Redis, если его там нет, устанавливая ttl.
    Если запрос уже сохранен возвращем ответ из Redis"""

    async def wrapper(request):
        timeout = 60
        redis = request.app['redis']
        url = str(request.url)
        record_exist = await redis.exists(url)
        if record_exist:
            response_data = await redis.get(url, encoding='utf-8')
            return web.Response(content_type='application/json',
                                text=response_data)
        else:
            res = await cor(request)
            await redis.set(url, res.text)
            await redis.expire(url, timeout)
            return res

    return wrapper


@redis_cache
async def post_list(request):
    """Создаем объект запроса sql_query, пердаем его в
    paginate и filter для обработки. Делаем запорс к базе"""
    response_data = {}
    sql_query = db.posts.select()
    try:
        sql_query = filter(request, sql_query)
        sql_query = paginate(request, sql_query, response_data)
    except ValueError:
        return web.HTTPBadRequest()

    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(sql_query)
        records = await cursor.fetchall()
        response_data['results'] = [dict(p) for p in records]
    return web.Response(content_type='application/json',
                        text=json.dumps(response_data, default=str))


@redis_cache
async def single_post(request):
    """Ищем объявление по переданному id"""
    optional_fields = request.query.get('fields', None)
    fields = ['name', 'price']
    if optional_fields is not None:
        fields.extend(optional_fields.split(','))
    post_id = int(request.match_info.get('id'))
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.posts.select().where(db.posts.c.id == post_id))
        record = await cursor.fetchone()
        # Если объявления с переданнными id не существует
        if record is None:
            return web.HTTPBadRequest()
        record = dict(record)
        try:
            response_data = dict((f, record[f]) for f in fields)
        except KeyError:
            return web.HTTPBadRequest()
        if not response_data.get('images', False):
            response_data['images'] = record['images'][0:1]

    return web.Response(content_type='application/json',
                        text=json.dumps(response_data, default=str))


async def create_post(request):
    """Создание объявления. Для валидации передавемых данных используем jsonschema"""
    data = await request.json()

    v = Draft3Validator(schema, format_checker=FormatChecker())
    if v.is_valid(data):
        async with request.app['db'].acquire() as conn:
            cursor = await conn.execute(db.posts.insert().values(**data))
            post_id = await cursor.fetchone()
        return web.HTTPCreated(body=json.dumps({'id': post_id[0]}),
                               content_type='application/json')
    else:
        response_data = {'errors': dict((err.path.pop(), err.message)
                                        for err in v.iter_errors(data))}
        return web.HTTPBadRequest(body=json.dumps(response_data),
                                  content_type='application/json')
