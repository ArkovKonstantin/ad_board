from api.views import PostView, SinglePostView


def setup_routes(app):
    app.router.add_view('/api/v1/posts', PostView)
    app.router.add_get(r'/api/v1/posts/{id:\d+}', SinglePostView)
