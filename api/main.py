import aiohttp_jinja2
import jinja2
from aiohttp import web

from models.recipes import get_recipes, get_recipe


async def hello(request):
    #data = await request.post()
    #context = {}
    #response = aiohttp_jinja2.render_template('recipe.html', request, context)
    #a = get_recipe('Стейк')
    return web.Response(text='OPPA')


async def recipe_all(request):
    """
    Это минимальная форма поиска и добовления рецепта, для удобства
    """
    context = {}
    response = aiohttp_jinja2.render_template('recipe.html', request, context)
    return response


async def recipes_data(request):
    """
    Возращает json список рецептов па запрашиваемым параметрам
    """
    data = await request.post()
    recipes = get_recipes(data)
    return web.Response(text=recipes)


async def recipe_data(request):
    """
    Возращает json рецепт по названию
    (нужно по id, потому что названия могут повторяться, но пока для удобства отсавлю так)
    """
    data = await request.post()
    recipe_ = get_recipe(data)
    return web.Response(text=recipe_)


# Тут просто мин проект с документации разростается чучуть.
app = web.Application()

aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader('templates')
)
# i added the styles, but it's just annoyed, and i turn them off
#app.add_routes([web.static('/static', 'static')])
app.add_routes([web.get('/', hello)])
app.add_routes([web.get('/recipe_all', recipe_all)])
app.add_routes([web.post('/recipe', recipes_data)])
app.add_routes([web.post('/recipes', recipe_data)])

web.run_app(app, host='127.0.0.1', port=5000)
