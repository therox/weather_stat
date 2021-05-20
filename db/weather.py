import datetime

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, Date
from geoalchemy2 import Geometry, WKTElement
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


engine = create_engine('postgresql://postgres:postgres@localhost/weather', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Lake(Base):
    __tablename__ = 'lake'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POINT', srid=SRID))
    temp = Column(Numeric)
    pressure = Column(Numeric)
    humidity = Column(Numeric)
    date = Column(Date, default=datetime.datetime)

    def __str__(self):
        return f"Lake at {self.geom}, temp: {self.temp}"


def save(lake: Lake):
    session = Session()
    session.add(lake)
    session.commit()


def query_point(x, y: float):
    session = Session()
    try:
        lake = session.query(Lake).filter(
            func.ST_Within(WKTElement(f'POINT({x} {y})', srid=SRID),
                           Lake.geom.ST_Buffer(10))).one()
    except:
        print('Not Found')
        return None

    print(f'\n\nFound: {lake}')

    session.commit()


if __name__ == '__main__':
    print("Ok")
    Lake.__table__.drop(engine)
    Lake.__table__.create(engine)
    save(Lake(geom=f'SRID={SRID}; POINT(1 0)', temp=5, pressure=12, humidity=12.6, date=datetime.datetime.now()))
    save(Lake(geom=f'SRID={SRID}; POINT(100 20)', temp=6, pressure=123, humidity=78, date=datetime.datetime.now()))

    # лезем в БД
    query_point(7, 5)
