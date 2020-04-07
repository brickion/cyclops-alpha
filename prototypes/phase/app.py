import config
import aiohttp
import apis
import pathlib
import play
from utils import(load_config, connect)
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

ROOT_PATH = pathlib.Path(__file__).parent.parent.parent


async def init(loop):
    logging.info('app started')
    conf = load_config(ROOT_PATH / 'config' / 'config.yml')
    connected = connect()
    session = aiohttp.ClientSession()
    if connected:
        data = await apis.fetch_assets(session, conf['api_base_url'])
        for item in data:
            config.saveFace(item.name, item.encoding)

    await play.run(conf, connected, session)
    await session.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))

try:
    loop.run_forever()
finally:
    loop.close()
