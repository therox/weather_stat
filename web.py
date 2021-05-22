from pyproj import Proj, transform
import requests
import datetime
from db import WeatherStat, SRID


def getHistoricalData(x, y: float, date_start, date_end: str, key: str):
    print(f"Converting POINT(4396) to POINT(4326)")
    inProj = Proj('epsg:4396')
    outProj = Proj('epsg:4326')
    lon, lat = transform(inProj, outProj, x, y, always_xy=True)
    print("Получили: ", lon, lat)
    try:
        # https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/52.06%2C-2.72/2018-2-4/2018-2-6?unitGroup=metric&key=
        print("Отправляем реквест")
        u = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lon}%2C{lat}/{date_start.strftime('%Y-%m-%d')}/{date_end.strftime('%Y-%m-%d')}"
        print(u)
        res = requests.get(u, params={'unitGroup': "metric", 'key': key})
        if res.status_code != 200:
            print(res.text)
            return
        print('Получили следующий документ: ', res.text)
        data = res.json()

        # print("Получили дней: ", len(data['days']))
        print("Парсим данные")
        # tempmax, tempmin, temp, humidity, pressure, datetime('%Y-%d-%m')

        for kk in data['days']:
            print(f'GEOM: SRID={SRID}; POINT({x} {y})')
            print(f'TEMP: {float(kk["temp"])}')
            print(f'TEMPMAX: {float(kk["tempmax"])}')
            print(f'TEMPMIN: {float(kk["tempmin"])}')
            print(f'PRESSURE: {float(kk["pressure"])}')
            print(f'HUMIDITY: {float(kk["humidity"])}')
            print(
                f'DATE: {datetime.datetime.strptime(kk["datetime"], "%Y-%m-%d").date()}'
            )

        d = [{
            'geom':
            f'SRID={SRID}; POINT({round(float(x), 4)} {round(float(y), 4)})',
            'temp':
            float(z['temp']),
            'tempmax':
            float(z['tempmax']),
            'tempmin':
            float(z['tempmin']),
            'pressure':
            float(z['pressure']),
            'humidity':
            float(z['humidity']),
            'date':
            datetime.datetime.strptime(z['datetime'], '%Y-%m-%d').date()
        } for z in data['days']]
        return (d)
    except Exception as e:
        print("Exception (find):", e)
        pass

    return None


if __name__ == '__main__':
    # getHistoricalData(37.618423, 55.751244, '1-02-2001', '01-02-2001',
    #                   'C99LPDXEB4A6UR3J3T6F9CB4S')

    # Москва
    getHistoricalData(-3833198.53891, 4587860.74166, '1-02-2001', '03-02-2001',
                      'C99LPDXEB4A6UR3J3T6F9CB4S')
