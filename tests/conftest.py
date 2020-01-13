import pytest
from api.main import init_app


@pytest.fixture
async def client(aiohttp_client):
    app = init_app()
    return await aiohttp_client(app)
