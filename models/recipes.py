import json

from peewee import fn, JOIN
from playhouse.shortcuts import model_to_dict

from models.models import Recipe, User, DishType, Likes


def get_recipes(required) -> json:
    """
    Получение списка рецептов по параметрам
    :param required: Параметры и порядок сортировки
    :return: Список рецептов json формата
    """
    recipes = process_request(required)
    recipe_json = []
    for recipe in recipes:
        recipe_json.append(create_json_recipe(recipe, 'list'))
    return json.dumps(recipe_json, ensure_ascii=False)


def get_recipe(required_recipe) -> json:
    """
    Получение полной информации о рецепте
    :param required_recipe: Название рецепта
    :return: рецепт json формата
    """
    recipe = Recipe.get(Recipe.name == required_recipe)
    recipe_json = create_json_recipe(recipe, 'solo')
    return json.dumps(recipe_json, ensure_ascii=False)


def create_json_recipe(recipe: Recipe, type_: str) -> dict:
    """
    Генерация словаря из экземпляра класса Recipe
    :param recipe: экземпляр класса Recipe
    :param type_: solo/list
    :return: Словарь с требуемыми параментрами
    """
    recipe_json = model_to_dict(recipe)
    if type_ == 'solo':
        pass
    elif type_ == 'list':
        del recipe_json['author']
        del recipe_json['steps']
    else:
        raise TypeError
    recipe_json['date'] = str(recipe_json['date'])
    recipe_json['likes'] = recipe.likes.count()
    recipe_json['dish_type'] = recipe_json['dish_type']['dish_type_name']
    return recipe_json


def process_request(data):
    """
    Обработать запрашиваемы параметры и создать итерируемый экземляр orm модели
    :param data: запрашиваемы параметры
    :return: итерируемый экземляр orm модели
    """
    recipes = Recipe.select().where(Recipe.active)
    if data['name']:
        recipes = recipes.where(Recipe.name.iregexp(data['name']))
    if data['hashtag']:
        recipes = recipes.where(Recipe.hashtags.iregexp(data['hashtag']))
    if data['user']:
        recipes = recipes.join(User).where(User.nickname == data['user'])
    if data['dish_type']:
        recipes = recipes.join(DishType, on=(Recipe.dish_type == DishType.id)).where(DishType.dish_type_name ==
                                                                                     data['dish_type'])
    if data['image']:
        recipes = recipes.where(Recipe.image.is_null(False))

    if data['order'] == 'date':
        recipes = recipes.order_by(Recipe.date)
    elif data['order'] == 'name':
        recipes = recipes.order_by(Recipe.name)
    elif data['order'] == 'id':
        recipes = recipes.order_by(Recipe.id)
    elif data['order'] == 'likes':
        recipes = recipes.select_extend(fn.COUNT(Likes.recipe).alias('count')).join(Likes, JOIN.LEFT_OUTER).\
            group_by(Recipe.id).order_by(-fn.COUNT(Likes.recipe).alias('count'))
    return recipes
