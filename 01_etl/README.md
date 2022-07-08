# Шаги для запуска этого проекта

1. Создайте свой собственный '.env' файл, или используйте '.env_example'
2. Запустите:
```
    $ docker-compose up --build
```
3. Откройте контейнер с БД и создайте схему 'content':
```
    $ docker exec -it database-container bash
    $ psql -U app -d movies_database
    $ CREATE SCHEMA IF NOT EXISTS content;
```
4. Мигрируйте модели в Джанго:
```
    $ docker exec web-container python3 manage.py migrate
```
5. Создайте суперюзера для админки в Джанго:
```
    $ docker exec web-container make superuser
```
6. Соберите файлы статики, которые будут отдаваться сервером Nginx:
```
    $ docker exec -it web-container bash
    $ python3 manage.py collectstatic
```

7. Опционально: Запустите ETL систему "Postgre -> ElasticSearch". Для этого используется файл
"docker-compose.dev.yml"
```
    $ docker-compose -f docker-compose.dev.yml up --build
    $ python3 etl/etl.py
```
8. Опционально: Перелейте данные о фильмах из Sqlite3 в Postgre. 
Для этого вам потребуется файл "docker-compose.dev.yml"
```
    $ docker-compose -f docker-compose.dev.yml up --build
```
Далее используйте скрипт load_data.py из модуля db_loader. Нам понадобится создать виртуальное 
окружение перед использованием загрузчика. Создадим его в папке 'service': 
```
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r service/requirements.txt
    $ python3 db_loader/load_data.py
```
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_cluster/settings -d '{ "transient": { "cluster.routing.allocation.disk.threshold_enabled": false } }'
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'