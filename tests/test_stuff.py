import json
from yarl import URL


async def test_post_list(client):
    """Тестирование получения списка объявлений"""
    url = '/api/v1/posts'
    resp = await client.get(url)

    assert resp.status == 200
    # Проверка ответа на соответсвие заданному формату
    resp_obj = json.loads(await resp.text())
    attrs = set(resp_obj.keys())
    assert attrs == {'results', 'next', 'prev'} or \
           attrs == {'results', 'next'}
    assert type(resp_obj['results']) == list


async def test_paginaton(client):
    """Тестирование пагинации"""
    page = 2
    limit = 5
    url = '/api/v1/posts?page={page}&limit={limit}'
    resp = await client.get(url.format(page=page, limit=limit))
    assert resp.status == 200
    resp_obj = json.loads(await resp.text())
    # Кол-во элементов меньше либо равно limit
    assert len(resp_obj['results']) <= limit
    # Сущесвуют ссылки next и prev и они корректны
    assert URL(resp_obj['next']).path_qs == url.format(page=page + 1, limit=limit)
    assert URL(resp_obj['prev']).path_qs == url.format(page=page - 1, limit=limit)


async def test_filter(client):
    """Тестирование фильтрации данных по убыванию и возрастанию"""

    async def _check(attr, flag):
        url = f'/api/v1/posts?filter[{attr}]={flag}'
        resp = await client.get(url)
        posts = (json.loads(await resp.text()))['results']
        prev_p = posts[0][attr]
        for idx in range(1, len(posts)):
            if prev_p is None or posts[idx][attr] is None:
                continue
            if flag == 'desc':
                assert posts[idx][attr] <= prev_p
            elif flag == 'asc':
                assert posts[idx][attr] >= prev_p
            prev_p = posts[idx][attr]

    # Сортировка по цене
    await _check('price', 'desc')
    await _check('price', 'asc')
    # Сортировка по дате
    await _check('pub_data', 'desc')
    await _check('pub_data', 'asc')


async def test_create_post(client):
    """Тестирование создания нового объявления"""
    invalid_json = {
        "name": 111,
        "description": 222,
        "price": 0,
        "images": [
            "image1",
            "image2",
            "image3",
            "image4"
        ]
    }
    url = f'/api/v1/posts'
    resp = await client.post(url, json=invalid_json)
    assert resp.status == 400
    # Валидный запрос
    valid_json = {
        "name": "item",
        "description": "item description",
        "price": 100,
        "images": [
            "image1",
            "image2",
            "image3"
        ]
    }
    resp = await client.post(url, json=valid_json)
    assert resp.status == 201

