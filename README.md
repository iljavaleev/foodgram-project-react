#Проект «Продуктовый помощник»

### Автор проекта
[Илья Валеев](https://github.com/iljavaleev/) 

---
## Описание проекта «Продуктовый помощник»
Это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие
рецепты в избранное и подписываться на публикации других авторов. Сервис 
«Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для 
приготовления выбранных блюд, и скачивать их в виде текстового файла.

---
## Основные endpoint'ы

* signup — регистрация пользователя.
* token — получение токена для аутентификации пользователя.
* users — работа с пользователями.
* recipes — работа с рецептами.
* tags — просмотр тегов.
* ingredients — просмотр ингридиентов.

## Используемые технологии
* Node.js
* Django REST Framework
* Djoser

## Инструкция по запуску проекта

Все операции выполняются в командной строке.


* Клонировать репозиторий:
```
git clone git@github.com:iljavaleev/foodgram-project-react.git
```

В дериктории infra/ cоздать файл .env, в котором указать переменные окружения для работы с базой данных:
```
cp .env.example .env
```

* Из дериктории infra/ запустить docker-compose командой:
```
docker-compose up -d --build
```

* Выполнить миграции:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

* Создать суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```

* При необходимости загрузить тестовую информацию из fixtures.json
```
docker-compose exec backend python manage.py runscript scripts.load_data
```
