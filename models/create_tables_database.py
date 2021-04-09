# Создание таблиц и связей базе данных
from models.models import db, DishType, User, Recipe, Likes, Favorites

with db:
    db.create_tables([DishType, User, Recipe, Likes, Favorites])

print('Tables are created')
