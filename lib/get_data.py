from __future__ import print_function
import platform
from time import sleep
import os
import stat
import datetime
import python_weather
import asyncio
import requests
import json

import os.path

import datetime as dt
from dateutil import tz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def convert_time(time, timezone):

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(timezone)
    utc = dt.datetime.strptime(time, '%H:%M')
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone).time()


def get_events():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        print("creds not valid")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        
        timezone = service.settings().get(setting='timezone').execute()['value']

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            yield(" ", "No events!")
        for event in events:
            start = str(event['start'].get('dateTime', event['start'].get('date')))
            time = str(convert_time(start[start.find('T') + 1: start.find('T') + 5], timezone))
            start = start.replace(start[start.find('T'):], " at: " + time)
            yield(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)



def isFifo():
    try:
        stat.S_ISFIFO(os.stat("/tmp/fifo").st_mode)
    except:
        return False
    finally:
        return True


def mem_write(str):
    if not isFifo():
        os.mkfifo("/tmp/fifo")

    fifo_read = open('/tmp/fifo', 'w') #0 without buffering
    fifo_read.write(str)
    fifo_read.close()


def mem_read():
    fifo_read = open('/tmp/fifo', 'r') #0 without buffering
    result = fifo_read.read()
    fifo_read.close()
    return result

async def getweather():
    with open('settings.json', 'r+') as f:
        data = json.load(f)
        city = data['city'] 
        state = data['state']
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    client = python_weather.Client(format=python_weather.METRIC)

    weather = await client.find(city + "," + state)
    await client.close()
    
    return (str(weather.current.sky_text) + " " + str(weather.current.temperature))

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

def end():
    local = ""
    if platform.system() == "Darwin":
        local = "local/"
    path = "/usr/" + local + "share/smartscreen/end"
    if os.path.exists(path) or os.path.exists("end"):
        return True
    return False

if __name__ == "__main__":
    fill_json()
    time = 0
    weather = ""
    loop = asyncio.get_event_loop()
    timer_max = 10
    while True:
        timer = timer_max
        while timer > 10:
            if end():
                break;
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            if time is not current_time:
                time = current_time
                mem_write(current_time)
            sleep(1)
            timer -= 1
        timer = timer_max
        if end():
            break;
        while timer > 10:
            if end():
                break;
            now = loop.run_until_complete(asyncio.gather(getweather()))[0]
            if weather is not now:
                weather = now
                weather += "C"
                mem_write(weather)
            sleep(1)
            timer -= 1
        timer = timer_max
        if end():
            break;
        while timer > 0:
            if end():
                break;
            events = list(get_events())
            if events[0][0] == " ":
                mem_write(events[0][1])
            else:
                for i in events:
                    event_data = str(i[0]).split('-')
                    month_of_event = str(event_data[1])
                    day_of_event = str(event_data[2].split('T')[0])
                    name_of_event = str(i[1]).rstrip()
                    mem_write(month_of_event + "|" + day_of_event + "|" + name_of_event)
            sleep(1)
            timer -= 1
        if end():
            break;
