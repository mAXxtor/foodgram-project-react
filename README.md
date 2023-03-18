<div id="header" align="center">
  <img src="https://media.giphy.com/media/BSsSBKN1eKGUU/giphy.gif" width="100"/>
</div>

# <div align="center"> Foodgram «Продуктовый помощник» </div>
Онлайн-сервис и API для него. Пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

Особенности:

- Просматривать рецепты
- Добавлять рецепты в избранное
- Добавлять рецепты в список покупок
- Создавать, удалять и редактировать собственные рецепты
- Скачивать список покупок

Временно доступен по [адресу](http://foodmax.zapto.org/)

## Технологии
[![foodgram_workflow](https://github.com/mAXxtor/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/mAXxtor/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
[![python version](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)
[![django version](https://img.shields.io/badge/Django-4.1-green)](https://www.djangoproject.com/)
![django rest framework version](https://img.shields.io/badge/Django%20REST%20Framework-3.14.0-green)
[![PostgreSQL](https://img.shields.io/badge/PostgresSQL-13.0-green)](https://www.postgresql.org/)
[![docker version](https://img.shields.io/badge/Docker-20.10-green)](https://www.docker.com/)
[![docker-compose version](https://img.shields.io/badge/Docker--Compose-3.8-green)](https://www.docker.com/)
[![nginx version](https://img.shields.io/badge/Nginx-%201.18-green)](https://nginx.org/ru/)
[![docker hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=515151)](https://www.docker.com/products/docker-hub)
[![github%20actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=515151)](https://github.com/features/actions)
[![yandex.cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=515151)](https://cloud.yandex.ru/)

## Workflow:
* tests - Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8). Дальнейшие шаги выполнятся только если push был в ветку master или main.
* build_and_push_to_docker_hub - Сборка и доставка docker-образа для контейнера на Docker Hub.
* deploy - Автоматический деплой проекта на удаленный сервер.
* send_message - Отправка уведомления о статусе workflow в Telegram через бота.
***- Для работы workflow:***
Добавить переменные среды окружения в [Secrets GitHub Actions](https://github.com/<username>/yamdb_final/settings/secrets/actions)
```
- SECRET_KEY=<ключ> # Cекретный ключ Django проекта (https://djecrety.ir/)
- ALLOWED_HOSTS=<'*'> # Разрешенные хосты/домены для которых работает Django проект (открыть доступ для всех - '*')
- DB_ENGINE=django.db.backends.postgresql # Движок базы данных
- DB_NAME=foodgram # Имя базы данных
- POSTGRES_USER=<login> # Имя пользователя для базы данных
- POSTGRES_PASSWORD=<password> # Пароль пользователя для базы данных
- DB_HOST=db # Название сервиса
- DB_PORT=5433 # Порт для подключения к базе данных
- DOCKER_USERNAME=<login> # Логин на Docker Hub
- DOCKER_PASSWORD=<password> # Пароль на Docker Hub
- HOST=<IP> # IP-адрес удаленного сервера
- USER=<login> # Логин на удаленном сервере
- PASSPHRASE=<password> # Пароль защиты SSH ключа на удаленном сервере (если требуется)
- SSH_KEY=<key> # Приватный ssh-ключ (публичный должен быть на сервере)
- TELEGRAM_TO=<id> # ID своего telegram аккаунта (https://t.me/userinfobot)
- TELEGRAM_TOKEN # Token telegram бота (https://t.me/BotFather, /token, имя бота)
- TEST_DB=<True/False> # Булево значение для подключения базы данных SQLlite (True) вместо PostgreSQL (False)
- DEBUG_MODE=<True/False> # Булево значение для включения режима отладки
CSRF_TRUSTED_ORIGINS=<Host name> # HTTPS адрес вашего сервера (ex. https://foodmax.zapto.org)
```

## Подготовка сервера:
Войти на свой удаленный сервер, установить и запустить [Docker](https://docs.docker.com/engine/install/) и [Docker-compose](https://docs.docker.com/compose/install/):
```
sudo apt install docker.io
sudo apt install docker-compose
sudo systemctl start docker
```
***- Для работы ssl сертификата установить certbot.***
Поочередно выполнить команды:
```
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
***- Создать рабочую директорию проекта и скачать в нее скрипт:***
```
mkdir foodgram && cd foodgram/
curl -L https://raw.githubusercontent.com/wmnnd/nginx-certbot/master/init-letsencrypt.sh > init-letsencrypt.sh
```
***- Отредактировать и запустить скрипт:***
Добавить домен в переменную domains и действующую электронную почту в переменную email:
```
nano init-letsencrypt.sh
```
Добавить разрешения на запуск скрипта и запустить его:
```
chmod +x init-letsencrypt.sh
sudo ./init-letsencrypt.sh
```
***- Cоздать и заполнить .env файл с переменными окружения в рабочей директории:***
```
ALLOWED_HOSTS=*
SECRET_KEY=5a!%1y_a6-odm+s=1wl_-8lyh%3ldtz7q=!@egrc9i&jza9!98
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=1105
DB_HOST=db
DB_PORT=5433
TEST_DB=False
DEBUG_MODE=False
CSRF_TRUSTED_ORIGINS=<Server DNS name or IP> (ex. https://foodmax.zapto.org/)
```

## Настройка и запуск приложения в контейнерах:
***- Клонировать репозиторий на локальный пк:***
```
git clone https://github.com/mAXxtor/foodgram-project-react.git
```
***- Скопировать файлы из директории infra/ на сервер:***
```
cd foodgram-project-react/infra
scp ./docker-compose.yml <username>@<host>:/home/<username>/foodgram/
scp ./nginx.conf <username>@<host>:/home/<username>/foodgram/default.conf
```
***- Развернуть контейнеры на удаленном сервере:***
Развернуть контейнеры через терминал на удаленном сервере:
```
sudo docker-compose up -d --build
```
***- Выполнить в контейнере backend миграции:***
```
sudo docker-compose exec backend python manage.py migrate
```
***- Создать суперпользователя:***
```
sudo docker-compose exec backend python manage.py createsuperuser
```
***- Собрать статику в volume static_value:***
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
***- Загрузить тестовые значения в базу данных:***
```
sudo docker-compose exec backend python manage.py load_test_data
```

### Endpoints:
```
POST /api/users/ - регистрация
POST /api/auth/token/login - создание токена
POST /api/auth/token/logout/ - удаление токена
GET /api/users/ - просмотр информации о пользователях

POST /api/users/set_password/ - изменение пароля
GET /api/users/{id}/subscribe/ - подписаться на пользователя
DEL /api/users/{id}/subscribe/ - отписаться от пользователя

POST /api/recipes/ - создать рецепт
GET /api/recipes/ - получить рецепты
GET /api/recipes/{id}/ - получить рецепт по id
DEL /api/recipes/{id}/ - удалить рецепт по id

GET /api/recipes/{id}/favorite/ - добавить рецепт в избранное
DEL /api/recipes/{id}/favorite/ - удалить рецепт из избранного

GET /api/users/{id}/subscribe/ - подписаться на пользователя
DEL /api/users/{id}/subscribe/ - отписаться от пользователя

GET /api/ingredients/ - получить список всех ингредиентов

GET /api/tags/ - получить список всех тегов

GET /api/recipes/{id}/shopping_cart/ - добавить рецепт в корзину
DEL /api/recipes/{id}/shopping_cart/ - удалить рецепт из корзины
```

### Примеры запросов к API:
**`POST` | Создание рецепта: `http://127.0.0.1:8000/api/recipes/`**

Request:
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
Response:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

**`POST` | Подписаться на пользователя: `http://127.0.0.1:8000/api/users/{id}/subscribe/`**

Response:
```
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```
