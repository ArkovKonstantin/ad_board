## API для сайта объявлений
### Реализованные методы и функции
 * Метод получения списка объявлений
 * Метод получения конкретного объявления
 * Метод создания объявления
 * Кэширование запросов в Redis
### Стек
 * aiohttp
 * sqlalchemy
 * aiopg
 * aioredis
 * jsonschema
 * pytest
### Запуск проекта
```$ git clone https://github.com/ArkovKonstantin/ad_board```<br>
```$ cd ad_board```<br>
```$ docker-compose up```<br>
После выполнения данных команд приложение будет доступно по адресу http://localhost:8001

### Запуск тестов 
```$ docker-compose exec api-server pytest```
### Структура проекта
 * ```api/main.py``` запуск сервера
 * ```ad_board.yaml``` конфигурация сервера для запуска из контейнера
 * ```dev.yaml``` конфигурация сервера локальной разработки
 * ```init_db.py``` создание таблиц и данных
 * ```tests/``` директория с тестами
 * ```schema.py``` схема валидации данных запросов
### Описание методов
Api задокументировано при помощи Swagger. Для просмотра спецификации api необходимо перейти по ссылке:
https://app.swaggerhub.com/apis/ArkovKonstantin/ad-board_api/1.0.0 <br> или открыть файл `openapi.yaml` в Swagger Editor (https://swagger.io/tools/swagger-editor/).
Примеры запросов можно найти в файле `request.http` или в `tests/test_stuff.py`


