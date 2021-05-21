from pyproj import Proj, transform
import requests
import datetime
from db import WeatherStat


def getHistoricalData(x, y: float, date_start, date_end: str, key: str):
    print(f"Converting POINT(4396) to POINT(4326)")
    inProj = Proj('epsg:4396')
    outProj = Proj('epsg:4326')
    lon, lat = transform(inProj, outProj, x, y, always_xy=True)
    d_start = datetime.datetime.strptime(date_start, '%d-%m-%Y')
    d_end = datetime.datetime.strptime(date_end, '%d-%m-%Y')
    print("Получили: ", lon, lat)
    try:
        # https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/52.06%2C-2.72/2018-2-4/2018-2-6?unitGroup=metric&key=
        print("Отправляем реквест")
        u = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lon}%2C{lat}/{d_start.strftime('%Y-%m-%d')}/{d_end.strftime('%Y-%m-%d')}"
        print(u)
        res = requests.get(u, params={'unitGroup': "metric", 'key': key})
        if res.status_code != 200:
            print(res.text)
            return
        data = res.json()

        # print("Получили дней: ", len(data['days']))
        print("Парсим данные")
        # tempmax, tempmin, temp, humidity, pressure, datetime('%Y-%m-%d')
        d = [{
            'temp': x['temp'],
            'tempmax': x['tempmax'],
            'tempmin': x['tempmin'],
            'humidity': x['humidity'],
            'pressure': x['pressure'],
            'date': x['datetime'],
        } for x in data['days']]
        print(d)
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
