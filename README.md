### <br>➜ https://dragunfoodgram.zapto.org/</br>

"Foodgram" - это инновационный веб-сайт для кулинарных энтузиастов, предоставляющий уникальную платформу для обмена и открытия рецептов. Здесь пользователи могут делиться своими кулинарными шедеврами, находить вдохновение в рецептах других участников и создавать собственные кулинарные коллекции.

## Цели проекта

Проект "Foodgram" стремится создать сообщество, объединяющее любителей готовить, где каждый сможет найти что-то новое и вдохновляющее для себя. Мы верим, что обмен рецептами помогает развивать личные кулинарные навыки и способствует культурному обмену через еду.

## Функционал

- **Публикация рецептов**: Зарегистрированные пользователи могут добавлять свои рецепты, включая описание, список ингредиентов и пошаговые инструкции.
- **Избранное**: Возможность добавлять понравившиеся рецепты в свой список избранного, чтобы всегда иметь быстрый доступ к любимым блюдам.
- **Подписки**: Подписывайтесь на других авторов, чтобы следить за их новыми публикациями и не пропускать интересные рецепты.
- **Список покупок**: Удобный сервис для зарегистрированных пользователей, который позволяет автоматически составлять список необходимых продуктов для выбранных рецептов. Это облегчит планирование покупок и приготовление пищи.


## Инструкции по запуску проекта:
1. **Клонировать репозиторий**:
   ```bash
   git clone git@github.com:EmilDragunov/foodgram.git
   ```

2. **Перейти в директорию проекта**:
   ```bash
   cd foodgram/backend/
   ```

3. **Создать и активировать виртуальное окружение** (для Windows):
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

4. **Установить зависимости**:
   ```bash
   pip install -r requirements.txt
   ```
   
5. **Создать файл `.env`** в корне проекта с настройками

6. **Запустить проект с помощью Docker**:
   ```bash
   docker compose -f docker-compose.production.yml up -d
   ```

7. **Выполнить миграции и собрать статику**:
   ```bash
   docker compose -f docker-compose.production.yml exec backend python manage.py migrate
   docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
   ```

8. **Создать суперпользователя**:
   ```bash
   docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
   ```

8. **Наполнить базу данных предустановленными данными**:
   ```bash
   docker compose -f infra/docker-compose.production.yml exec backend python manage.py loaddata data/fixtures.json
   ```

## Примеры API-запросов

Примеры запросов, доступных через API:

- **Получение списка рецептов**:
  ```http
  GET /api/recipes/
  ```

- **Добавление рецепта в избранное**:
  ```http
  POST /api/recipes/{id}/favorite/
  Headers:
    Authorization: Bearer <токен>
  ```

- **Получение списка ингредиентов**:
  ```http
  GET /api/ingredients/
  ```

## Документация к API по ссылке:
 ```http
  https://dragunfoodgram.zapto.org/api/docs
  ```

### Автор работы
[Эмиль Драгунов](https://github.com/EmilDragunov) <br>
[telegram: @emildragunov](https://t.me/emildragunov)
