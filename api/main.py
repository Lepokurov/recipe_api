import json

import aiohttp_jinja2
import jinja2
from aiohttp import web

from api.items.auth import CurrentUser, authorization, login, register, logout
from api.items.recipe_items import recipe_form, get_recipe, get_recipes_list, add_recipe, block_recipe, unblock_recipe, \
    like_recipe, favorite_recipe, get_recipes_list_favorites, delete_recipe, change_recipe
from api.items.user_items import user_form, block_user, unblock_user, upd_user, get_users_list, get_user, delete_user


async def menu(request):
    if CurrentUser.authorized or CurrentUser.admin:
        context = {'nickname': CurrentUser.nickname}
    else:
        context = {'nickname': 'Not authorized'}
    response = aiohttp_jinja2.render_template('index.html', request, context)
    return response


async def make_app() -> web.Application:
    app = web.Application()

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader('templates')
    )
    # forms
    app.add_routes([web.get('/authorization', authorization)])
    app.add_routes([web.get('/recipe_form', recipe_form)])
    app.add_routes([web.get('/user_form', user_form)])
    app.add_routes([web.get('/', menu)])

    app.add_routes([web.get('/login', login)])
    app.add_routes([web.post('/registration', register)])
    app.add_routes([web.get('/logout', logout)])

    app.add_routes([web.put('/block_recipe', block_recipe)])
    app.add_routes([web.put('/unblock_recipe', unblock_recipe)])
    app.add_routes([web.put('/block_user', block_user)])
    app.add_routes([web.put('/unblock_user', unblock_user)])

    app.add_routes([web.get('/get_recipe', get_recipe)])
    app.add_routes([web.get('/get_recipes_list', get_recipes_list)])
    app.add_routes([web.get('/get_recipes_list_favorites', get_recipes_list_favorites)])
    app.add_routes([web.post('/add_recipe', add_recipe)])
    app.add_routes([web.post('/like_recipe', like_recipe)])
    app.add_routes([web.post('/favorite_recipe', favorite_recipe)])
    app.add_routes([web.put('/change_recipe', change_recipe)])
    app.add_routes([web.delete('/delete_recipe', delete_recipe)])

    app.add_routes([web.get('/get_user', get_user)])
    app.add_routes([web.get('/get_users_list', get_users_list)])
    app.add_routes([web.put('/update_user', upd_user)])
    app.add_routes([web.delete('/delete_user', delete_user)])
    return app


web.run_app(make_app(), host='127.0.0.1', port=5000)
