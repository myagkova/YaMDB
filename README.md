# YaMDb
(https://github.com/github/docs/actions/workflows/main.yml/badge.svg)


### Описание
Проект **YaMDb** собирает отзывы пользователей на произведения. 
Произведения делятся на категории _(Category)_ : _«Книги», «Фильмы», «Музыка»_. Список категорий может быть расширен.

Сами произведения в **YaMDb** не хранятся, здесь нельзя посмотреть фильм или послушать музыку. 

Произведению _(Title)_ может быть присвоен жанр _(Genre)_ из списка предустановленных (например, _«Сказка»_, _«Рок»_ или _«Артхаус»_). 

Новые жанры может создавать только администратор. Благодарные или возмущённые читатели оставляют к произведениям текстовые отзывы _(Review)_ и выставляют произведению рейтинг (оценку в диапазоне от одного до десяти). Из множества оценок автоматически высчитывается средняя оценка произведения.

### Запуск приложения:
* Собрать контейнеры и запустить их
  ```
  docker-compose up -d --build
  ```
* Сделать миграции
  ```
  docker-compose exec web python manage.py makemigrations --noinput
  docker-compose exec web python manage.py migrate --noinput
  ```
* Создать суперпользователя
  ```
  docker-compose exec web python manage.py createsuperuser
  ```
* Подгрузить статику
  ```
  docker-compose exec web python manage.py collectstatic --no-input
  ```
* Заполненить базы начальными данными
  ```
  docker-compose exec web python manage.py dumpdata > fixtures.json
  ```




