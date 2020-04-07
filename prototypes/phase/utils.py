import yaml
import urllib.request
from datetime import datetime


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.safe_load(f)
    return data


def format_datetime(timestamp):
    pass

# check network connection
def connect(host='https://www.baidu.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
