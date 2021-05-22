import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, Date
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import simplejson

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
    tempmax = Column(Numeric)
    tempmin = Column(Numeric)
    pressure = Column(Numeric)
    humidity = Column(Numeric)
    date = Column(Date, default=datetime.datetime.now())

    def __str__(self):
        return f"WeatherStat at {to_shape(self.geom)}, temp: {self.temp} for {self.date.strftime('%d-%m-%Y')}"

    def as_dict(self):
        return {
            'geom': to_shape(self.geom).__str__(),
            'temp': float(self.temp),
            'tempmax': float(self.tempmax),
            'tempmin': float(self.tempmin),
            'pressure': float(self.pressure),
            'humidity': float(self.humidity),
            'date': self.date.strftime('%d-%m-%Y')
        }
        # return {
        #     c.name: getattr(self, c.name)
        #     for c in self.__table__.columns if c.name != 'geom'
        # }


def save(ws: WeatherStat):
    session = Session()
    session.add(ws)
    session.commit()


def query_point(x, y: float, d_start, d_end: datetime) -> WeatherStat:
    session = Session()
    print(
        f"Ищем точки вблизи POINT({x}, {y}) на даты c {d_start.strftime('%d-%m-%Y')} по {d_end.strftime('%d-%m-%Y')}"
    )
    try:
        w = session.query(WeatherStat).filter(
            func.ST_Within(WKTElement(f'POINT({x} {y})', srid=SRID),
                           WeatherStat.geom.ST_Buffer(10)),
            WeatherStat.date >= d_start, WeatherStat.date <= d_end).order_by(
                WeatherStat.date.asc()).distinct(WeatherStat.date)
    except Exception as e:
        print(e)
        return None
    return w


def create_fixtures():
    # Москва в 4396
    x, y = -3833198.53891, 4587860.74166

    save(
        WeatherStat(geom=f'SRID={SRID}; POINT({x} {y})',
                    temp=12,
                    tempmax=17,
                    tempmin=7,
                    pressure=12,
                    humidity=12.6,
                    date=datetime.datetime.now()))
    save(
        WeatherStat(geom=f'SRID={SRID}; POINT({x+5} {y})',
                    temp=15,
                    tempmax=20,
                    tempmin=3,
                    pressure=12,
                    humidity=12.6,
                    date=datetime.datetime.now()))
    save(
        WeatherStat(geom=f'SRID={SRID}; POINT({x} {y-5})',
                    temp=10,
                    tempmax=19,
                    tempmin=-1,
                    pressure=12,
                    humidity=12.6,
                    date=datetime.datetime.now()))
    save(
        WeatherStat(geom=f'SRID={SRID}; POINT({x} {y})',
                    temp=6,
                    tempmax=10,
                    tempmin=-1,
                    pressure=123,
                    humidity=78,
                    date=datetime.datetime.now() - datetime.timedelta(days=1)))
    save(
        WeatherStat(geom=f'SRID={SRID}; POINT({x} {y})',
                    temp=6,
                    tempmax=13,
                    tempmin=3,
                    pressure=123,
                    humidity=78,
                    date=datetime.datetime.now() - datetime.timedelta(days=2)))


if __name__ == '__main__':
    WeatherStat.__table__.drop(engine, checkfirst=True)

    WeatherStat.__table__.create(engine)
    create_fixtures()

    x, y = -3833198.53891, 4587860.74166
    k_list = query_point(
        x, y,
        datetime.datetime.now().date() - datetime.timedelta(days=7),
        datetime.datetime.now().date())
    found = []
    if k_list:

        for k in k_list:
            found.append(k.as_dict())
        print(f'Всего найдено {len(found)} записей в БД')
        print(json.dumps(found))
    else:
        print('Not Found. Requesting api')
