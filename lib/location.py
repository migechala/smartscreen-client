import requests
import json
def fill_json():

    res = requests.get("http://ipinfo.io")

    city = res.json()['city']
    state = res.json()['region']

    with open('settings.json', 'r+') as f:
        data = json.load(f)
        data['city'] = city
        data['state'] = state
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
fill_json()