#!/bin/sh

# uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
uwsgi --ini wsgi.ini
# http://127.0.0.1:5000/?x=2&y=3&start=1-2-2021&end=1-2-2001