#!/bin/sh

#Запускаем постгрес
#su - docker -c "/usr/lib/postgresql/9.3/bin/postgres -D /var/lib/postgresql/9.3/main -c config_file=/etc/postgresql/9.3/main/postgresql.conf"
cd /app
# uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
env LANG=en_US.utf8
env LC_ALL=en_US.UTF-8
env LC_LANG=en_US.UTF-8

uwsgi --ini wsgi.ini
# http://127.0.0.1:5000/?x=2&y=3&start=1-2-2021&end=1-2-2001

# Запуск докера: podman run -it --rm -p 9090:9090 weather
# Запуск докера с постгисом: podman run --name some-postgis -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgis/postgis