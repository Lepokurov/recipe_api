import json

from peewee import fn, JOIN
from playhouse.shortcuts import model_to_dict

from models.models import User, db, Recipe


def get_users_list_(data):
    """
    Достать список пользователей
    :param data: по recipes/likes
    :return: список пользователей
    """
    users = User.select().where(User.active).limit(10)
    user_list = []
    if data == 'recipes':
        recipe_count = fn.COUNT(Recipe.id).alias('recipes')
        users = users.select_extend(recipe_count). \
            join(Recipe, JOIN.LEFT_OUTER, on=(Recipe.author == User.id)). \
            group_by(User.id).order_by(-recipe_count)
    elif data == 'likes':
        pass

    for user in users:
        user_list.append(__create_json_user(user))

    return json.dumps(user_list, ensure_ascii=False)


def get_user_(nickname, authorization=False):
    """
    Достать пользователя
    :param nickname: никнейм
    :param authorization: Если авторизация, то другой ответ
    :return: json ответ с полями пользователя
    """
    try:
        user = User.get(User.nickname == nickname)
        if authorization:
            user_json = __create_json_auth_user(user)
        else:
            user_json = __create_json_user(user)
    except Exception as e:
        error_message = str(e).split('\n')[0]
        user_json = {'error': error_message}
    if not authorization:
        user_json = json.dumps(user_json, ensure_ascii=False)
    return user_json


def add_user_(nickname):
    """
    Добавить пользователя
    :param nickname: никнейм
    :return: json ответ с полями нового пользователя
    """
    try:
        with db.atomic():
            user = User.create(nickname=nickname, active=True)
            user.save()
        user_json = __create_json_auth_user(user)
    except Exception as e:
        error_message = str(e).split('\n')[0]
        user_json = {'error': error_message}

    return user_json


def upd_user_(data, current_user):
    """
    Изменить пользователя
    :param data: параменты
    :param current_user: пользователь
    :return: ответ как прошла операция
    """
    try:
        nickname = data['nickname']
        user = User.update({User.nickname: nickname}).where(User.nickname == current_user.nickname)
        success = user.execute()
        if success:
            response = {'status': nickname + ' user blocked'}
        else:
            # Я не знаю как тут может сломатся
            response = {'error': 'error'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return json.dumps(response)


def delete_user_(current_user):
    """
    Удалить пользователя
    :param current_user: пользователь
    :return: ответ как прошла операция
    """
    try:
        nickname = current_user.nickname
        user = User.get(nickname=nickname)
        success = user.delete_instance(recursive=True)
        if success:
            response = {'success': nickname + ' user is deleted'}
        else:
            # тут я тоже не знаю что может ломаться
            response = {'error': 'error'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return response


def block_user_(nickname):
    """
    Заблокировать пользователя
    :param nickname: никней пользователя
    :return: ответ как прошла операция
    """
    try:
        user = User.update({User.active: False}).where(User.nickname == nickname)
        success = user.execute()
        if success:
            response = {'status': nickname + ' user blocked'}
        else:
            response = {'error': 'probably wrong name'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return response


def unblock_user_(nickname):
    """
    Разблокировать пользователя
    :param nickname: никней пользователя
    :return: ответ как прошла операция
    """
    try:
        user = User.update({User.active: True}).where(User.nickname == nickname)
        success = user.execute()
        if success:
            response = {'status': nickname + ' user unblock'}
        else:
            response = {'error': 'probably wrong name'}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        response = {'error': error_message}
    return response


def __create_json_auth_user(user):
    user_json = {
        'id': user.id,
        'nickname': user.nickname
    }
    return user_json


def __create_json_user(user):
    if user.active:
        user_json = model_to_dict(user)
        user_json['recipes'] = user.recipe_set.count()
    else:
        user_json = {'error': 'user is blocked'}
    return user_json
