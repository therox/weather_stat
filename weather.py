import datetime
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def weather():
    x = request.args.get('x')
    y = request.args.get('y')
    start = request.args.get('start')
    end = request.args.get('end')
    if x is None:
        return 'Ошибка!', 400
    try:
        d_start = datetime.datetime.strptime(start, '%d-%m-%Y')
        d_end = datetime.datetime.strptime(end, '%d-%m-%Y')
    except Exception as e:
        print(e)
        return 'Неверный формат даты: ДД-ММ-ГГГГ'
    # Правим, если перепутаны даты
    if d_start > d_end:
        d_start, d_end = d_end, d_start
    return f'Получена точка POINT({x} {y}, дата начала: {d_start.strftime("%d-%m-%Y")}, дата окончания: {d_end.strftime("%d-%m-%Y")})'


if __name__ == "__main__":
    app.run()
    #app.run(host='0.0.0.0')