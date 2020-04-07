import datetime
from aiohttp import FormData


async def create_asset(session, base_url, asset_info, encoding, img, site='eb5d84ca610ea3b5355fa8bb', source='py-app'):
    api_path = base_url + '/assets'
    data = FormData()
    data.add_field('name', str(asset_info))
    data.add_field('hash', str(asset_info))
    data.add_field('encoding', str(encoding))
    data.add_field('site', site)
    data.add_field('source', source)
    data.add_field('file', img)

    async with session.post(api_path, data=data) as response:
        return await response.json()


async def create_event(session, base_url, asset, site, value, event_type='temperature'):
    api_path = base_url + '/events'
    data = {'asset': asset, 'site': site, 'value': value, 'type': event_type}
    async with session.post(api_path, data=data) as response:
        return await response.json()


async def fetch_assets(session, base_url):
    api_path = base_url + '/assets/sources/'+'py-app'
    async with session.get(api_path) as response:
        return await response.json()


def log(action, item):
    print(str(datetime.datetime.now()))
    print(action + ' ' + item)
