import logging
from aiohttp import web


def redis_cache(cor):
    """Сохраненяем GET запрос в Redis, если его там нет, устанавливая ttl.
    Если запрос уже сохранен возвращем ответ из Redis"""

    async def wrapper(self):
        timeout = 60
        redis = self.request.app['redis']
        url = str(self.request.url)
        record_exist = await redis.exists(url)
        if record_exist:
            logging.debug('Return response from Redis Cache')
            response_data = await redis.get(url, encoding='utf-8')
            return web.Response(content_type='application/json',
                                text=response_data)
        else:
            res = await cor(self)
            await redis.set(url, res.text)
            await redis.expire(url, timeout)
            return res

    return wrapper
