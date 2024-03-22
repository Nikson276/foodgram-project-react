# Foodgram

## О проекте 
Это — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## How to deploy
*Initial deploy*
- Скопируйте на сервер в директорию taski/ файл docker-compose.production.yml.
    - при помощи утилиты SCP
        - `scp -i path_to_SSH/SSH_name docker-compose.production.yml \ 
	username@server_ip:/home/username/taski/docker-compose.production.yml`
    - с помощью редактора nano создать файл `docker-compose.production.yml`
- Запуск контейнеров
    - `sudo docker compose -f docker-compose.production.yml up`
- Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:
    - `sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate`
    - `sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic`
    - `sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/`
- Запустите фикстуры
    - `sudo docker compose -f docker-compose.production.yml exec backend python manage.py load.csv`
- Проверьте доступность, откройте страницу https://ваш_домен/admin/

*Updates*
- push to master --> will start CI&CD

## API
[Redoc](docs\redoc.html)

## Технологии
* Frontend — SPA-приложение на React.
* Backend - Django + DRF
* DB - PostgreSQL
* Infrastructure - Docker, NGINX

## Хост
Public IP 130.193.54.101
Domain: https://foodgram-nikson.serveblog.net/

### Admin cred's for reviewer (TO DELETE)
superuser
Username: admin
Email address: admin@admin.ru
fw9S3YJsyLG5Zjw

## Об авторе
[Никита Михайлов](https://github.com/Nikson276)
Студент Yandex Practicum
Back-end developer
