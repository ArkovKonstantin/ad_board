import json
import logging

from aiohttp import web
from api import db
from api.schema import schema
from jsonschema import Draft3Validator, FormatChecker
from api.utils import redis_cache


class PostView(web.View):
    def __init__(self, request, page=None, limit=None, sorting_args=None):
        super().__init__(request)
        if page is not None:
            self.page = page
        if limit is not None:
            self.limit = limit
        if sorting_args is not None:
            self.sorting_args = sorting_args

    @redis_cache
    async def get(self):
        """Создаем объект запроса sql_query, пердаем его в
            paginate и filter для обработки. Делаем запорс к базе"""
        response_data = {}
        sql_query = db.posts.select()
        sql_query = self._sort(sql_query)
        sql_query, next_p, prev_p = self._paginate(sql_query)
        response_data['next'] = next_p
        if prev_p:
            response_data['prev'] = prev_p
        # Make request to DB
        async with self.request.app['db'].acquire() as conn:
            logging.debug(f'Make SQL query "{sql_query}"')
            cursor = await conn.execute(sql_query)
            records = await cursor.fetchall()
            response_data['results'] = [dict(p) for p in records]
        return web.Response(content_type='application/json',
                            text=json.dumps(response_data, default=str))

    async def post(self):
        """Создание объявления. Для валидации передавемых данных используем jsonschema"""
        data = await self.request.json()

        v = Draft3Validator(schema, format_checker=FormatChecker())
        if v.is_valid(data):
            async with self.request.app['db'].acquire() as conn:
                cursor = await conn.execute(db.posts.insert().values(**data))
                post_id = await cursor.fetchone()
            return web.HTTPCreated(body=json.dumps({'id': post_id[0]}),
                                   content_type='application/json')
        else:
            response_data = {'errors': dict((err.path.pop(), err.message)
                                            for err in v.iter_errors(data))}
            return web.HTTPBadRequest(body=json.dumps(response_data),
                                      content_type='application/json')

    def _paginate(self, sql_query):  # TODO last page
        offset = (self.page - 1) * self.limit
        next_p = f'{self.request.url.scheme}://{self.request.url.host}:{self.request.url.port}' \
                 f'{self.request.url.path}?page={self.page + 1}&limit={self.limit}'
        prev_p = None
        if self.page > 1:
            prev_p = f'{self.request.url.scheme}://{self.request.url.host}:{self.request.url.port}' \
                     f'{self.request.url.path}?page={self.page - 1}&limit={self.limit}'
        return sql_query.limit(self.limit).offset(offset), next_p, prev_p

    def _sort(self, sql_query):
        if self.sorting_args:
            return sql_query.order_by(*self.sorting_args)
        else:
            return sql_query


class SinglePostView(web.View):
    def __init__(self, request, optional_fields=None):
        super().__init__(request)
        self.optional_fields = optional_fields

    @redis_cache
    async def get(self):
        """Ищем объявление по переданному id"""
        fields = ['name', 'price']
        if self.optional_fields is not None:
            fields.extend(self.optional_fields)
        post_id = int(self.request.match_info.get('id'))
        async with self.request.app['db'].acquire() as conn:
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
