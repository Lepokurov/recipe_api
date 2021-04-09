import json

import aiohttp_jinja2
from aiohttp import web

from api.items.auth import no_authorization_error, CurrentUser, no_admin_error

from models.recipe import get_recipes_list_, add_recipe_, get_recipe_, block_recipe_, unblock_recipe_, like_to_recipe_, \
    favorite_recipe_, get_recipes_list_favorites_, delete_recipe_, upd_recipe_


async def recipe_form(request):
    """
    форма рецепта для удобства
    """
    if CurrentUser.authorized or CurrentUser.admin:
        context = {'nickname': CurrentUser.nickname}
    else:
        context = {'nickname': 'Not authorized'}
    response = aiohttp_jinja2.render_template('recipe.html', request, context)
    return response


async def get_recipes_list(request):
    """
    Возращает json список рецептов па запрашиваемым параметрам
    """
    if CurrentUser.authorized:
        data = request.query_string
        recipes = get_recipes_list_(data)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def get_recipes_list_favorites(request):
    """
    Разблокировать пользователя по никнейму
    """
    if CurrentUser.authorized:
        recipes = get_recipes_list_favorites_(CurrentUser)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def add_recipe(request):
    """
    Создает новый рецепт
    """
    if CurrentUser.authorized:
        try:
            # jsons
            data = await request.json()
        except:
            # form_data
            data = await request.post()
        recipes = add_recipe_(data, CurrentUser)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def get_recipe(request):
    """
    Возращает json рецепт по названию
    (нужно по id, потому что названия могут повторяться, но для удобства и наглядности я сделал на именах)
    """
    if CurrentUser.authorized:
        name = request.query_string.split('=')[1]
        recipe = get_recipe_(name)
    else:
        recipe = no_authorization_error()
    return web.Response(text=recipe)


async def like_recipe(request):
    """
    Пользователь ставит лайк рецепту
    """
    if CurrentUser.authorized:
        # Я не могу это вынести в отдельную функцию, он пишет что это корутина и ничего не возвращает
        try:
            # jsons
            data = await request.json()
        except:
            # form_data
            data = await request.post()
        recipes = like_to_recipe_(data, CurrentUser)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def favorite_recipe(request):
    """
    Пользователь добавит рецепт в избранное
    """
    if CurrentUser.authorized:
        try:
            # jsons
            data = await request.json()
        except:
            # form_data
            data = await request.post()
        recipes = favorite_recipe_(data, CurrentUser)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def change_recipe(request):
    """
    Пользователь изменит свой рецепт
    """
    if CurrentUser.authorized:
        try:
            # jsons
            data = await request.json()
        except:
            # form_data
            data = await request.post()
        name = request.query_string.split('=')[1]
        recipes = upd_recipe_(name, data, CurrentUser)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def delete_recipe(request):
    """
    Пользователь удалит свой рецепт
    """
    if CurrentUser.authorized:
        name = request.query_string.split('=')[1]
        recipes = delete_recipe_(name, CurrentUser)
    else:
        recipes = no_authorization_error()
    return web.Response(text=recipes)


async def block_recipe(request):
    """
    Заблокировать пользователя по никнейму
    """
    if CurrentUser.admin:
        name = request.query_string.split('=')[1]
        text_message = block_recipe_(name)
    else:
        text_message = no_admin_error()
    text_message = json.dumps(text_message)
    return web.Response(text=text_message)


async def unblock_recipe(request):
    """
    Разблокировать пользователя по никнейму
    """
    if CurrentUser.admin:
        name = request.query_string.split('=')[1]
        text_message = unblock_recipe_(name)
    else:
        text_message = no_admin_error()
    text_message = json.dumps(text_message)
    return web.Response(text=text_message)
