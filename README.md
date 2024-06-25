Foodgram - площадка, позволяющая пользователям делиться рецептами, добавлять их в избранное, а так же вносить ингредиенты в список покупок.

В проекте использован стек технологий:
Python 3.9, Django, Docker, Gunicorn, Nginx, Postgres.

Для запуска ресурса на сервере создаём директорию /foodgram/:
```
sudo mkdir foodgram
```
и командой
```
cd foodgram
```
переходим в директорию /foodgram/ и создаём файлы .env, docker-compose.yml и nginx.conf
```
sudo touch .env
sudo touch docker-compose.yml
sudo touch nginx.conf
```
Затем из директории infra копируем содержимое файлов nginx.conf, docker-compose.yml.
В файл .env записываем секреты:
```
DB_ENGINE=django.db.backends.posgtgresql
POSTGRES_DB=foodgram
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=ключ от джанго-проекта
DEBUG=False
```
Для деплоя через github actions в настройках записываем секреты:
```
DB_ENGINE=django.db.backends.posgtgresql
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY='ключ от джанго-проекта'
DEBUG=False
DOCKER_USERNAME=логин от докерхаба
DOCKER_PASSWORD=пароль от докерхаба
SSH_KEY=*
PASSPHRASE=*
TELEGRAM_TO=id телеграм профиля
TELEGRAM_TOKEN=токен бота телеграм
```
Далее командами устанавливаем docker на наш сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```
и запускаем наш проект на сервере(обязательно находиться в директории /foodgram/)
```
sudo docker compose up -d
```
Выполняем миграции и собираем статику:
```
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
```
Создаём пользователя с правами суперюзера:
```
sudo docker compose exec backend python manage.py createsuperuser
```
Создаём теги: 'Breakfast', 'Lunch', 'Dinner' с помощью админ панели или заполняем менеджером сожержимое из файла data/tags.csv
```
sudo docker compose exec python manage.py create_tags
```
и наполняем ингредиентами БД из файла data/ingredients.csv
```
sudo docker compose exec python manage.py import_ingredients
```
Для остановки контейнеров используем команду:
```
sudo docker compose down
```
