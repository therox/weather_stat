#!/bin/sh

echo "CREATE DATABASE weather;" | psql -h ${PG_HOST} -U postgres 
echo "CREATE EXTENSION postgis;" | psql -h ${PG_HOST} -U postgres weather
python3 /app/db.py