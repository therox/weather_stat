# weather_stat

Для запуска необходимо иметь 2 докер-образа:

1. postgis/postgis
2. докер с реализацией задачи


## Описание
Реализовать функцию получения статистических данных по погоде в заданной точке по заданному интервалу времени.

Отслеживаемые данные:
* tempmax - максимальная суточная температура,
* tempmin - минимальная суточная температура
* temp - средняя суточная температура
* humidity - влажность
* pressure - давление
* date - дата

Что делает программа:

1. Ищет в БД записи, лежащие от заданной пользователем координаты на расстоянии не более 10 метров в указанном промежутке времени
1. Если записи не найдены (все или частично), то запрашивает у сервиса данные на эти дни. Данные проверяются и отсутствующие в первоначальном запросе сохраняются в БД
1. Повторно запрашивает записи из п.1 и отдаёт результат пользователю

## Подготовка

Скачиваем докер-образ с постгисом
> docker pull postgis/postgis 

Создаём docker-образ c задачей на основе fedora
> docker build -t weather -f Dockerfile_weather

Запускаем docker с postgis: 
> docker run --name postgis -p 5432:5432 -e POSTGRES_PASSWORD=`postgres` -d postgis/postgis

Запуск докера с задачей в режиме создания БД и таблицы (после запуска данной команды в БД заносятся 3 тестовые записи для Москвы за 3 последних дня): 
> docker run -it --rm -e PG_HOST=`10.10.10.3` -e PGPASSWORD=`postgres` -p 9090:9090 weather sh /app/create_db.sh

## Работа

Запускаем докер с задачей
> docker run -it --rm -e PG_HOST=`10.10.10.3` -e PGPASSWORD=`postgres` -e API_KEY=123456789ABCDEF -p 9090:9090 weather

Идём в браузер и пробуем достучаться до API следующим запросом (в примере указаны данные Москвы):
> http://127.0.0.1:9090/?x=-3833188.53891&y=4587860.74166&start=21-05-2021&end=23-5-2021

При успешном запросе, вернется информация в следующем виде:
```
[
    {
        "geom": "POINT (-3833198.5389 4587860.7416)",
        "temp": 6.0,
        "tempmax": 13.0,
        "tempmin": 3.0,
        "pressure": 123.0,
        "humidity": 78.0,
        "date": "21-05-2021"
    },
    {
        "geom": "POINT (-3833198.5389 4587858.7416)",
        "temp": 6.0,
        "tempmax": 10.0,
        "tempmin": -1.0,
        "pressure": 123.0,
        "humidity": 78.0,
        "date": "22-05-2021"
    },
    {
        "geom": "POINT (-3833196.5389 4587861.7416)",
        "temp": 12.0,
        "tempmax": 17.0,
        "tempmin": 7.0,
        "pressure": 12.0,
        "humidity": 12.6,
        "date": "23-05-2021"
    }
]
```

Описание параметров окружения:
* PG_HOST - ip-адрес машины, на которой запущены докеры. При старте докера с постгисом, автоматически пробрасывается порт 5432 наружу
* POSTGRES_PASSWORD - пароль пользователя postgres для работы с БД (только контейнер с постгисом)
* PGPASSWORD - пароль пользователя postgres для работы с БД (только контейнер с задачей)
* API_KEY - ключ разработчика для работы с сервисом visualcrossing.com (только контейнер с задачей)

В качестве провайдера данных из интернета выбран API от visualcrossing.com, с небольшим количеством бесплатных запросов в день (порядка 20-30)

PS: Тестирование проводилось на OS Fedora с ПО `podman` (аналог `docker`)

PS: В задаче используется докер с БД PostgreSQL без перманентного сохранения данных. При желании, можно воспользоваться локальной БД с соответствующими изменениями параметров окружения, передаваемому докеру weather. Можно изменить только хост и пароль пользователя postgres для работы с БД - это было сделано для того, чтобы не усложнять проверку/тест