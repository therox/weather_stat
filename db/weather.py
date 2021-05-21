import datetime

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, Date
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

SRID = 4396
# Таблица weather, состоящая из следующих колонок:
# 1) geom        - геометрия
# 2) temperature - температура
# 3) pressure    - Давление
# 4) humidity    - Влажность
# 5) date        - дата

# SRID=4326;POINT (1 2)

# CREATE TABLE weather (
#     id         serial PRIMARY KEY,
#     geom       GEOMETRY NOT NULL,
#     temp       numeric NOT NULL,
#     pressure   numeric NOT NULL,
#     humidity   numeric NOT NULL,
#     date       date
# );

engine = create_engine('postgresql://postgres:postgres@localhost/weather',
                       echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class WeatherStat(Base):
    __tablename__ = 'weather_stat'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POINT', srid=SRID))
    temp = Column(Numeric)
    pressure = Column(Numeric)
    humidity = Column(Numeric)
    date = Column(Date, default=datetime.datetime)

    def __str__(self):
        return f"Lake at {self.geom}, temp: {self.temp}"


def save(lake: WeatherStat):
    session = Session()
    session.add(lake)
    session.commit()


def query_point(x, y: float) -> WeatherStat:
    session = Session()
    try:
        w = session.query(WeatherStat).filter(
            func.ST_Within(WKTElement(f'POINT({x} {y})', srid=SRID),
                           WeatherStat.geom.ST_Buffer(10))).one()
    except:
        return None
    return w


if __name__ == '__main__':
    print("Ok")
    WeatherStat.__table__.drop(engine, checkfirst=True)

    WeatherStat.__table__.create(engine)
    save(
        WeatherStat(geom=f'SRID={SRID}; POINT(1 0)',
                    temp=5,
                    pressure=12,
                    humidity=12.6,
                    date=datetime.datetime.now()))
    save(
        WeatherStat(geom=f'SRID={SRID}; POINT(100 100)',
                    temp=6,
                    pressure=123,
                    humidity=78,
                    date=datetime.datetime.now()))

    # лезем в БД
    k = query_point(93, 93)
    if k:
        print('Found: ', k)
        print(to_shape(k.geom))
    else:
        print('Not Found. Requesting api')
