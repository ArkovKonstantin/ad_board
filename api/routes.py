from views import handle


def setup_routes(app):
    app.router.add_get('/api/v1/posts', handle)
