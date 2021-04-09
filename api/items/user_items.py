import json

import aiohttp_jinja2
from aiohttp import web

from api.items.auth import no_authorization_error, CurrentUser, no_admin_error, logout_user

from models.user import get_user_, get_users_list_, block_user_, unblock_user_, upd_user_, delete_user_


async def user_form(request):
    """
    Это минимальная форма пользователей, для удобства
    """
    if CurrentUser.authorized or CurrentUser.admin:
        context = {'nickname': CurrentUser.nickname}
    else:
        context = {'nickname': 'Not authorized'}
    response = aiohttp_jinja2.render_template('user.html', request, context)
    return response


async def get_user(request):
    """
    Возращает json пользователя по никнейму
    """
    if CurrentUser.authorized:
        nickname = request.query_string.split('=')[1]
        user = get_user_(nickname)
    else:
        user = no_authorization_error()
    return web.Response(text=user)


async def get_users_list(request):
    """
    Возращает json список рецептов па запрашиваемым параметрам
    """
    if CurrentUser.authorized:
        data = request.query_string.split('=')[1]
        user = get_users_list_(data)
    else:
        user = no_authorization_error()
    return web.Response(text=user)


async def upd_user(request):
    """
    Изменить свой ник
    """
    if CurrentUser.authorized:
        try:
            # jsons
            data = await request.json()
        except:
            # form_data
            data = await request.post()
        text_message = upd_user_(data, CurrentUser)
    else:
        text_message = no_authorization_error()
    text_message = json.dumps(text_message, ensure_ascii=False)
    return web.Response(text=text_message)


async def delete_user(request):
    """
    Удалить себя
    """
    if CurrentUser.authorized:
        text_message = delete_user_(CurrentUser)
        logout_user()
    else:
        text_message = no_authorization_error()
    text_message = json.dumps(text_message, ensure_ascii=False)
    return web.Response(text=text_message)


async def block_user(request):
    """
    Заблокировать рецепт по названию
    """
    if CurrentUser.admin:
        nickname = ''
        data = request.query_string.split('=')
        if data[0] == 'nickname':
            nickname = data[1]
        text_message = block_user_(nickname)
    else:
        text_message = no_admin_error()
    text_message = json.dumps(text_message, ensure_ascii=False)
    return web.Response(text=text_message)


async def unblock_user(request):
    """
    Разблокировать рецепт по названию
    """
    if CurrentUser.admin:
        nickname = ''
        data = request.query_string.split('=')
        if data[0] == 'nickname':
            nickname = data[1]
        text_message = unblock_user_(nickname)
    else:
        text_message = no_admin_error()
    text_message = json.dumps(text_message, ensure_ascii=False)
    return web.Response(text=text_message)
