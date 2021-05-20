import psycopg2

# Таблица weather, состоящая из следующих колонок:
# 1) geom        - геометрия
# 2) temperature - температура
# 3) pressure    - Давление
# 4) humidity    - Влажность
# 5) date        - дата

# SRID=4326;POINT (1 2)

# CREATE TABLE weather (
#     id        serial PRIMARY KEY,
#     geom       GEOMETRY NOT NULL,
#     temp         numeric NOT NULL,
#     pressure   numeric NOT NULL,
#     humidity        numeric NOT NULL,
#     date         date
# );

conn = psycopg2.connect(dbname='weather_stat',
                        user='postgres',
                        password='postgres',
                        host='localhost')
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO weather (geom, temp, pressure, humidity, date) VALUES ('SRID=4326;POINT (1 2)', 24, 765.3, 46, now())"
)

cursor.execute('SELECT * FROM weather LIMIT 10')
records = cursor.fetchall()
print(records[0])

cursor.close()
conn.close()
