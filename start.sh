#!/bin/sh

#Запускаем постгрес
su - docker -c "/usr/lib/postgresql/9.3/bin/postgres -D /var/lib/postgresql/9.3/main -c config_file=/etc/postgresql/9.3/main/postgresql.conf"

# uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
uwsgi --ini wsgi.ini
# http://127.0.0.1:5000/?x=2&y=3&start=1-2-2021&end=1-2-2001