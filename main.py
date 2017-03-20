import asyncio

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiopg.sa import create_engine
import sqlalchemy as sa

metadata = sa.MetaData()


data_table = sa.Table('data_table', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('value', sa.String(255)))


async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXISTS data_table')
        await conn.execute('CREATE TABLE data_table (id serial PRIMARY KEY, value varchar(255))')


async def init_pg(app):
    engine = await create_engine(
        database='async_test',
        user='async_test',
        password='async_test',
        host='127.0.0.1',
        loop=app.loop)
    app['db'] = engine
    await create_table(app['db'])


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


class MainView(web.View):

    @aiohttp_jinja2.template('index.html')
    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            cursor = await conn.execute(data_table.select())
            result = await cursor.fetchall()
        return {'data': result}

    @aiohttp_jinja2.template('index.html')
    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            data = await self.request.post()
            value = data.get('string', '')
            await conn.execute(data_table.insert().values(value=value))
        return web.HTTPFound(location='/')


def main():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('async', 'templates'))
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    app.router.add_route('*', '/', MainView)
    web.run_app(app, host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
