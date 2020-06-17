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

# ENDPOINT = 'https://health-federation.pellar.io'
ENDPOINT = 'http://localhost:3000'

def create_asset(asset_info,encoding,img,site='0c77477f9822d9353099cbb2'):
    api_path = ENDPOINT + '/assets'
    data = {'name':asset_info, 'hash':asset_info, 'encoding': encoding, 'site':site}
    files={'file':img}
    response_raw = requests.post(url = api_path, data=data,files=files)
    log('RESPONSE', response_raw.text)
    log('POST', api_path)
    response = response_raw.json()

    if response['result'] == 'SUCCESS':
        return response['key']
    else:
        return None

def create_event(id, event):
    api_path = ENDPOINT + '/assets' + id
    response = requests.post(url = api_path)
    print(response)
    return '123'

def load_users(site_id):
    api_path = ENDPOINT + '/assets'
    response = requests.get(url = api_path)
    print(response)
    return '123'

def log(action, item):
    print(str(datetime.datetime.now()))
    print(action + ' ' + item)
