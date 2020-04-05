import requests
import datetime

ENDPOINT = 'https://health-federation.pellar.io'
# ENDPOINT = 'http://localhost:3000'

def create_asset(asset_info,encoding,img,site='eb5d84ca610ea3b5355fa8bb'):
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
