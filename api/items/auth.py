import json

import aiohttp_jinja2
from aiohttp import web

from models.user import get_user_, add_user_
# Я убил огромное количество времени чтобы использовать aiohttp.ClientSession() но ничего не рабоатет,
# я не понимаю как тут работает сессия
# По этому написал такой интерфейс, чтобы потом можно было безболезненно (наверно) изменить этот модуль


class CurrentUser:
    id: int
    nickname: str
    authorized = False
    admin = False


def login_user(user_data):
    CurrentUser.id = user_data['id']
    CurrentUser.nickname = user_data['nickname']
    CurrentUser.authorized = True
    CurrentUser.admin = False


def logout_user():
    CurrentUser.authorized = False
    CurrentUser.admin = False


def login_admin():
    CurrentUser.nickname = 'Admin'
    CurrentUser.admin = True
    CurrentUser.authorized = False


def no_authorization_error():
    error = {'error': 'not authorization'}
    return json.dumps(error)


def no_admin_error():
    error = {'error': 'not admin'}
    return error


async def authorization(request):
    """
    Это минимальная форма для авторизиции/регестрации
    """
    if CurrentUser.authorized or CurrentUser.admin:
        context = {'nickname': CurrentUser.nickname}
    else:
        context = {'nickname': 'Not authorized'}
    response = aiohttp_jinja2.render_template('login.html', request, context)
    return response


async def login(request):
    """
    Если такой пользователь существует - авторизация, не сущетвует - ошибка
    """
    nickname = request.query_string.split('=')[1]
    if nickname == 'admin':
        login_admin()
        user_data = {'nickname': 'admin'}
    else:
        user_data = get_user_(nickname, True)
        if 'error' not in user_data:
            login_user(user_data)

    json_user = json.dumps(user_data, ensure_ascii=False)
    return web.Response(text=json_user)


async def register(request):
    """
    Если такого пользователя не существует - создание и авторизация, сущетвует - ошибка
    """
    data = await request.post()
    nickname = data['nickname']
    if nickname == 'admin':
        return web.Response(text='Reserved name')
    user_data = add_user_(nickname)
    login_user(user_data)
    json_user = json.dumps(user_data, ensure_ascii=False)
    return web.Response(text=json_user)


async def logout(request):
    """
    выход
    """
    if CurrentUser.authorized:
        logout_user()
        text_message = 'exit is done'
    else:
        text_message = 'Not authorized'
    return web.Response(text=text_message)
