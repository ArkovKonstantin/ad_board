## API для сайта объявлений
### Реализованные методы и функции
 * Метод получения списка объявлений
 * Метод получения конкретного объявления
 * Метод создания объявления
 * Кэширование запросов в Redis
### Стэк
 * aiohttp
 * sqlalchemy
 * aiopg
 * aioredis
 * jsonschema
 * pytest
### Запуск проекта
```git clone https://github.com/ArkovKonstantin/ad_board```<br>
```cd ad_board```<br>
```$ docker-compose up```
### Запуск тестов 
```$ docker-compose exec api-server pytest```
### Структура проекта
 * ```api/main.py``` запуск сервера
 * ```ad_board.yaml``` конфигурация сервера
 * ```init_db.py``` создание таблиц и данных
 * ```tests/``` директория с тестами
 * ```schema.py``` схема валидации данных запросов
