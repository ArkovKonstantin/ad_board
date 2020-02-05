from aiohttp import web
from api.settings import config
from sqlalchemy import desc, asc
from api.views import PostView, SinglePostView


@web.middleware
async def process_req_param(request, handler):
    if handler == PostView:
        if request.method == 'GET':
            page = request.query.get('page', None)
            limit = request.query.get('limit', None)
            # Get page from query
            if page is None:
                page = 1
            else:
                if page.isdigit():
                    page = int(page)
                    if page < 1:
                        return web.HTTPBadRequest(text='page must be > 1')
                else:
                    return web.HTTPBadRequest(text='page must be integer')
            # Get limit from query
            if limit is None:
                limit = config['posts_per_page']
            else:
                if limit.isdigit():
                    limit = int(limit)
                    if limit >= config['max_posts_per_page']:
                        return web.HTTPBadRequest(text=f'limit must lower than {config["max_posts_per_page"]}')
                else:
                    return web.HTTPBadRequest(text='limit must be integer')
            # Get sorted parameters (column and order)
            # ex: http://host/path?sort[col1]=asc&sort[col2]=desc
            sorting_args = []
            for key in request.query:
                if key.startswith('sort'):  # query can contain several columns for sorting
                    _, col = key[:-1].split('[')
                    if request.query[key] == 'desc':
                        sorting_args.append(desc(col))
                    elif request.query[key] == 'asc':
                        sorting_args.append(asc(col))
                    else:
                        return web.HTTPBadRequest(text='the sort[col] parameter value can be asc or desc')

            return await handler(request, page, limit, sorting_args)
    # Get optional fields for displaying single post
    elif handler == SinglePostView:
        if request.method == 'GET':
            possible_fields = {'images', 'pub_date', 'description'}
            optional_fields = request.query.get('fields', None)
            if optional_fields is not None:
                optional_fields = optional_fields.split(',')
                # Check fields
                for f in optional_fields:
                    if f not in possible_fields:
                        return web.HTTPBadRequest(text=f'{f} field does not exist')

            return await handler(request, optional_fields)

    return await handler(request)
