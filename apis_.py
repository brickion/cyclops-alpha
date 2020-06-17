import requests

def log_person(id):
    ENDPOINT = 'http://localhost:3000/people/' + id + '/visit'
    response = requests.post(url = ENDPOINT)
    print(response)
    return
