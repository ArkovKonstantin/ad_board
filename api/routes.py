from api.views import post_list, create_post, single_post


def setup_routes(app):
    app.router.add_get('/api/v1/posts', post_list)
    app.router.add_post('/api/v1/posts', create_post)
    app.router.add_get(r'/api/v1/posts/{id:\d+}', single_post)
