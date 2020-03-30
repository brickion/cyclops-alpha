import requests
import datetime

# ENDPOINT = 'http://theia-federation-stage2.ap-southeast-1.elasticbeanstalk.com'
ENDPOINT = 'http://localhost:3000'

def create_asset(asset_info,encoding,img,site='python_demo'):
    api_path = ENDPOINT + '/assets'
    data = {'name':asset_info,'hash':asset_info,'encoding': encoding,'site':site}
    files={'file':img}
    response_raw = requests.post(url = api_path, data=data,files=files)
    response = response_raw.json()
    log('POST', api_path)
    log('RESPONSE', response_raw.text)
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
