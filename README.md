# Javstva

Javstva - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

## Технологии:
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL

## Запуск проекта на локальной машине:
* Клонировать репозиторий:
```
git clone https://github.com/silifonov/foodgram.git
```
* В директории infra создать файл *.env* и заполнить своими данными по аналогии с *.env.example*
* Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, созданию суперпользователя.
* После запуска проект будут доступен по адресу: http://localhost/
* Документация будет доступна по адресу: http://localhost/api/docs/
