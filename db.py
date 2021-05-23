import datetime
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, Date
from geoalchemy2 import Geometry, WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# Идентификатор проекции
SRID = 4396

# Получаем из окружения хост и пароль для доступа к postgreSQL
pg_host = 'localhost'
env_pg_host = os.getenv('PG_HOST')
if env_pg_host != None:
    pg_host = env_pg_host

pg_password = 'postgres'
env_pg_password = os.getenv('PGPASSWORD')
if env_pg_password != None:
    pg_password = env_pg_password

# Создаём связь алхимии с постгресом
engine = create_engine(
    f'postgresql://postgres:{pg_password}@{pg_host}/weather', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class WeatherStat(Base):
    """Основной класс, представляющий работу с таблицей со погодной сводкой"""
    __tablename__ = 'weather_stat'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POINT', srid=SRID))
    temp = Column(Numeric)
    tempmax = Column(Numeric)
    tempmin = Column(Numeric)
    pressure = Column(Numeric)
    humidity = Column(Numeric)
    date = Column(Date, default=datetime.datetime.now())

    def from_dict(data: dict):
        print("Got dict: ", data)
        return WeatherStat(geom=data['geom'],
                           temp=data['temp'],
                           tempmax=data['tempmax'],
                           tempmin=data['tempmin'],
                           pressure=data['pressure'],
                           humidity=data['humidity'],
                           date=data['date'])

    def __str__(self):
        return f"WeatherStat at {self.geom}, temp: {self.temp} for {self.date.strftime('%d-%m-%Y')}"

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


def save(ws: WeatherStat):
    """Функция сохранения записи в БД"""
    session = Session()
    session.add(ws)
    session.commit()


def query_point(x, y: float, d_start, d_end: datetime) -> WeatherStat:
    """Запрос к БД
    Параметры:
    ----------
    x, y : float
        Координаты точки
    d_start, d_end : datetime
        Даты начала и конца периода запроса
    """
    session = Session()
    print(
        f"Searching for points near POINT({x}, {y}) from {d_start.strftime('%d-%m-%Y')} to {d_end.strftime('%d-%m-%Y')}"
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
    """
    Создание фикстур

    Параметры:
    ----------
    x, y : float
        Координаты точки
    d_start, d_end : datetime
        Даты начала и конца периода запроса
    """
    # Москва в 4396
    # x, y = -3833198.53891, 4587860.74166
    x, y = -3833198.5389, 4587860.7416

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
