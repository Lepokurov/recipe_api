from peewee import *
import datetime
# Тут на мой вгляд нечего комментировать. Я просто описываю сущности.

db = PostgresqlDatabase('recipe', user='postgres', password='admin', host='127.0.0.1', port=5432)


def get_date_now():
    now = datetime.datetime.now()
    date_now = str(now.year) + '.' + str(now.month) + '.' + str(now.day)
    return date_now


class BaseModel(Model):

    class Meta:
        database = db


class DishType(BaseModel):
    dish_type_name = CharField(unique=True, null=False)

    class Meta:
        db_table = 'dish_type'


class User(BaseModel):
    id = PrimaryKeyField(unique=True)
    nickname = CharField(unique=True, null=False)
    active = BooleanField()

    class Meta:
        db_table = 'user'
        order_by = 'id'


class Recipe(BaseModel):
    id = PrimaryKeyField(unique=True)
    author = ForeignKeyField(User)
    name = CharField(null=False)
    date = DateField(default=get_date_now())
    description = TextField()
    steps = TextField()
    image = CharField()
    dish_type = ForeignKeyField(DishType)
    # Наверно лучше было создать отдельную хештег таблицу и + многие к многим
    hashtags = TextField()
    active = BooleanField()

    class Meta:
        db_table = 'recipe'
        order_by = 'id'


class Likes(BaseModel):
    user = ForeignKeyField(User, backref='likes')
    recipe = ForeignKeyField(Recipe, backref='likes')

    class Meta:
        db_table = 'likes'


class Favorites(BaseModel):
    user = ForeignKeyField(User, backref='favorites')
    recipe = ForeignKeyField(Recipe, backref='favorites')

    class Meta:
        db_table = 'favorites'
