import json

from peewee import fn, JOIN
from playhouse.shortcuts import model_to_dict

from models.models import Recipe, User, DishType, Likes, db, Favorites


def get_recipes_list_(required) -> json:
    """
    Получение списка рецептов по параметрам
    :param required: Параметры и порядок сортировки
    :return: Список рецептов json формата
    """
    recipes = __process_request(required)
    recipe_list = []
    for recipe in recipes:
        recipe_list.append(__create_json_recipe(recipe, 'list'))
    return json.dumps(recipe_list, ensure_ascii=False)


def get_recipe_(required_recipe: str) -> json:
    """
    Получение полной информации о рецепте
    :param required_recipe: Название рецепта
    :return: рецепт json формата
    """
    try:
        recipe = Recipe.get(Recipe.name == required_recipe)
        recipe_json = __create_json_recipe(recipe)
    except Exception as e:
        # Я не могу взять только текст ошибки из е, нет отдельного атрибута
        # а так он расписывает многа букав, и сложна букавы читать
        error_message = str(e).split('\n')[0]
        recipe_json = {'error': error_message}

    return json.dumps(recipe_json, ensure_ascii=False)


def add_recipe_(data, user):
    """
    Добавление рецепта пользователем
    :param data: Поля Рецента
    :param user: Пользователь, добавивший рецепт
    :return: json - добавленный элемент или текст ошибки.
    """
    try:
        with db.atomic():
            recipe = Recipe.create(
                author_id=User.get(nickname=user.nickname),
                name=data['name'],
                description=data['description'],
                steps=data['steps'],
                image=data['image'],
                dish_type=DishType.get(dish_type_name=data['dish_type']),
                hashtags=data['hashtag'],
                active=True
            )
            recipe.save()
        recipe_json = __create_json_recipe(recipe)
    except Exception as e:
        error_message = str(e).split('\n')[0]
        recipe_json = {'error': error_message}

    return json.dumps(recipe_json, ensure_ascii=False)


def upd_recipe_(name_recipe, data, user):
    """
    изменить свой рецепт
    :param name_recipe: name of recipe to change
    :param user: Пользователь, уто пытается изменть рецепт
    :param data: put параметр 'name'
    :return: ответ как прошла операция
    """
    try:
        recipe = Recipe.get(name=name_recipe)
        if recipe.author.nickname == user.nickname:
            update = {}
            if 'name' in data and data['name']:
                update[Recipe.name] = data['name']
            if 'description' in data and data['description']:
                update[Recipe.description] = data['description']
            if 'hashtags' in data and data['hashtags']:
                update[Recipe.hashtags] = data['hashtags']
            if 'steps' in data and data['steps']:
                update[Recipe.steps] = data['steps']
            if 'dish_type' in data and data['dish_type']:
                update[Recipe.dish_type] = DishType.get(dish_type_name=data['dish_type'])
            if 'image' in data and data['image']:
                update[Recipe.hashtag] = data['image']

            recipe = Recipe.update(update).where(Recipe.name == name_recipe)
            success = recipe.execute()
            if success:
                response = {'status': 'recipe changed'}
            else:
                response = {'error': 'recipe no changed'}
        else:
            response = {'error': 'u not owner of this recipe'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return json.dumps(response, ensure_ascii=False)


def delete_recipe_(name, user):
    """
    изменить свой рецепт
    :param user: Пользователь, кто пытается удалить рецепт
    :param name: название рецепты
    :return: ответ как прошла операция
    """
    try:
        recipe = Recipe.get(name=name)
        if recipe.author.id == user.id:
            success = recipe.delete_instance(recursive=True)
            if success:
                response = {'success': name + ' recipe is deleted'}
            else:
                response = {'error': 'probably wrong name'}
        else:
            response = {'error': 'u not owner of this recipe'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return json.dumps(response, ensure_ascii=False)


def block_recipe_(name):
    """
    Заблокирать рецепт
    :param name: название рецепта
    :return: ответ как прошла операция
    """
    try:
        recipe = Recipe.update({Recipe.active: False}).where(Recipe.name == name)
        success = recipe.execute()
        if success:
            response = {'status': name + ' recipe blocked'}
        else:
            response = {'error': 'probably wrong name'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return response


def unblock_recipe_(name):
    """
    Разблокирать рецепт
    :param name: название рецепта
    :return: ответ как прошла операция
    """
    try:
        recipe = Recipe.update({Recipe.active: True}).where(Recipe.name == name)
        success = recipe.execute()
        if success:
            response = {'status': name + ' recipe unblock'}
        else:
            response = {'error': 'probably wrong name'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return response


def like_to_recipe_(data, user):
    """
    Поставить рецепту лайк пользователем
    :param data: post параметр 'name'
    :param user: пользователь
    :return: ответ как прошла операция
    """
    try:
        with db.atomic():
            recipe = data['name']
            # Я просто по приколу так написал вместо джоина 'рецепт' таблицы, не думал что будет работать.
            # только под конец написания узнал
            like, new_like = Likes.get_or_create(recipe=Recipe.get(Recipe.name == recipe), user=user.id)
            if new_like:
                like.save()
                response = {'success': recipe+' like is added'}
            else:
                response = {'error': 'like is already added'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}

    return json.dumps(response, ensure_ascii=False)


def favorite_recipe_(data, user):
    """
    Добавить рецепт в избранное пользователя
    :param data: post параметр 'name'
    :param user: пользователь
    :return: ответ как прошла операция
    """
    try:
        recipe = data['name']
        with db.atomic():
            # Я просто по приколу так написал вместо джоина 'рецепт' таблицы, не думал что будет работать.
            # только под конец написания узнал
            favorite, new_favorite = Favorites.get_or_create(recipe=Recipe.get(Recipe.name == recipe), user=user.id)
            if new_favorite:
                favorite.save()
                response = {'success': recipe + ' added to favorites'}
            else:
                response = {'error': "it's already favorite"}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}

    return json.dumps(response, ensure_ascii=False)


def get_recipes_list_favorites_(current_user):
    """
    Получить список избранных рецптов пользователя
    :param current_user: ПОльзователь
    :return: json список рецептов
    """
    user = User.get(nickname=current_user.nickname)
    favorites = user.favorites
    recipe_list = []
    for favorite in favorites:
        recipe = favorite.recipe
        if recipe.active:
            recipe_list.append(__create_json_recipe(recipe, 'list'))
    return json.dumps(recipe_list, ensure_ascii=False)


def __create_json_recipe(recipe: Recipe, type_='solo') -> dict:
    """
    Генерация словаря из экземпляра класса Recipe
    :param recipe: экземпляр класса Recipe
    :param type_: solo/list
    :return: Словарь с требуемыми параментрами
    """
    if recipe.active:
        recipe_json = model_to_dict(recipe)
        if type_ == 'list':
            del recipe_json['steps']
        recipe_json['date'] = str(recipe_json['date'])
        recipe_json['likes'] = recipe.likes.count()
        recipe_json['dish_type'] = recipe_json['dish_type']['dish_type_name']
    else:
        recipe_json = {'error': 'recipe is blocked'}
    return recipe_json


def __process_request(raw_data: str):
    """
    Обработать запрашиваемые параметры и создать итерируемый экземляр orm модели
    :param raw_data: запрашиваемые get (через &) параметры
    :return: итерируемый экземляр orm модели
    """
    data = __normalize_get_request(raw_data)
    recipes = Recipe.select().where(Recipe.active)
    # если есть ключ и в нем есть значение тогда накладывай условия выбора.
    if 'name' in data and data['name']:
        recipes = recipes.where(Recipe.name.iregexp(data['name']))
    if 'hashtags' in data and data['hashtags']:
        recipes = recipes.where(Recipe.hashtags.iregexp(data['hashtags']))
    if 'user' in data and data['user']:
        recipes = recipes.join(User).where(User.nickname == data['user'])
    if 'dish_type' in data and data['dish_type']:
        recipes = recipes.join(DishType, on=(Recipe.dish_type == DishType.id)).where(DishType.dish_type_name ==
                                                                                     data['dish_type'])
    if 'image' in data and data['image']:
        recipes = recipes.where(Recipe.image.is_null(False))

    if 'order' in data:
        if data['order'] == 'date':
            recipes = recipes.order_by(Recipe.date)
        elif data['order'] == 'name':
            recipes = recipes.order_by(Recipe.name)
        elif data['order'] == 'id':
            recipes = recipes.order_by(Recipe.id)
        elif data['order'] == 'likes':
            likes_count = fn.COUNT(Likes.recipe).alias('count')
            recipes = recipes.select_extend(likes_count).\
                join(Likes, JOIN.LEFT_OUTER,  on=(Likes.recipe == Recipe.id)).\
                group_by(Recipe.id).order_by(-likes_count)
    return recipes


def __normalize_get_request(raw_data: str) -> dict:
    """
    Из сроки в словарь для удобства
    """
    data = {}
    for param in raw_data.split('&'):
        key = param.split('=')[0]
        value = param.split('=')[1]
        data[key] = value
    return data
