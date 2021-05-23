#!/bin/sh

su - -c "export PG_HOST=${PG_HOST}; export PGPASSWORD=${PGPASSWORD}; export API_KEY=${API_KEY}; cd /app; uwsgi --ini wsgi.ini"

# Пример запроса:
# http://127.0.0.1:9090/?x=-3833188.53891&y=4587860.74166&start=13-05-2021&end=20-5-2021

# Запуск докера с постгисом: 
# > podman run --name postgis -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgis/postgis
# Запуск докера для создания БД: 
# > podman run -it --rm -e PG_HOST=10.10.10.3 -e PGPASSWORD=postgres -p 9090:9090 weather sh /app/create_db.sh
# Запуск докера: 
# > podman run -it --rm -e PG_HOST=10.10.10.3 -e PGPASSWORD=postgres -p 9090:9090 weather
