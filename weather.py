import datetime
import json
from web import getHistoricalData
from db import WeatherStat, query_point, save
from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/')
def weather():
    """
    Получение погоды

    Параметры:
    ----------
    x, y : float
        координаты точки в метрах
    start, end : str
        начало и конец периода в формате ДД-ММ-ГГГГ
    """

    # Конвертируем входные параметры в правильный формат
    x = request.args.get('x')
    y = request.args.get('y')
    start = request.args.get('start')
    end = request.args.get('end')
    if x is None:
        return 'Error!', 400
    try:
        d_start = datetime.datetime.strptime(start, '%d-%m-%Y')
        d_end = datetime.datetime.strptime(end, '%d-%m-%Y')
    except Exception as e:
        print(e)
        return 'Incorrect date format: ДД-ММ-ГГГГ'
    # Правим, если перепутаны даты
    if d_start > d_end:
        d_start, d_end = d_end, d_start
    print(
        f'Got POINT({round(float(x), 4)} {round(float(y), 4)}, start date: {d_start.strftime("%d-%m-%Y")}, end_date: {d_end.strftime("%d-%m-%Y")})'
    )
    # Запрашиваем БД на предмет заданных данных
    k_list = query_point(x, y, d_start, d_end)
    found = []
    if k_list:
        found = (ws_list_to_dict_list(k_list))

        if len(found) < (d_end - d_start).days + 1:
            # К нам пришли не все данные запускаем вытаскиваетель данных с сайта
            hd = getHistoricalData(x, y, d_start, d_end,
                                   'C99LPDXEB4A6UR3J3T6F9CB4S')
            # Получили данные, теперь идём по всем данным и новые сохраняем в БД и добавляем к предыдущему результату
            # Проходимся по всем датам
            for dat1 in (d_start + datetime.timedelta(n)
                         for n in range((d_end - d_start).days + 1)):
                # Смотрим, есть ли данные за эту дату в результатах
                ws_found = next((item for item in found
                                 if item["date"] == dat1.strftime('%d-%m-%Y')),
                                None)
                if ws_found is None:
                    print('Not found. Searching in API results')
                    # Ищем то же самое в найденном в интырнете
                    web_res = next(
                        (item for item in hd if item['date'] == dat1.date()),
                        None)
                    if web_res is not None:
                        # Сохраняем в БД
                        print('Saving to DB')
                        save(WeatherStat.from_dict(web_res))
                    else:
                        print('Not found at all')
    # Еще разок запрашиваем данные из БД
    k_list = query_point(x, y, d_start, d_end)
    if k_list:
        found = (ws_list_to_dict_list(k_list))

        resp = Response(json.dumps(found))
        resp.headers['Content-Type'] = 'application/json'
        return resp
    return 'Records not found', 404


def ws_list_to_dict_list(ws_list: list[WeatherStat]) -> list[dict]:
    """
    Конвертируем массив WeatherStat в словарь для выдачи клиенту
    """
    found = []
    for ws in ws_list:
        found.append(ws.as_dict())
    return found


if __name__ == "__main__":
    app.run()
    #app.run(host='0.0.0.0')