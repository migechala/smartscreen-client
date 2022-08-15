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
from smartscreen import get_events
import os.path


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

    fifo_read = open('/tmp/fifo', 'w')  # 0 without buffering
    fifo_read.write(str)
    fifo_read.close()


def mem_read():
    fifo_read = open('/tmp/fifo', 'r')  # 0 without buffering
    result = fifo_read.read()
    fifo_read.close()
    return result


async def getweather():
    try:
        with open('settings.json', 'r+') as f:
            data = json.load(f)
            city = data['city']
            state = data['state']
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        async with python_weather.Client(format=python_weather.METRIC) as client:
            weather = await client.get(city + "," + state)
    except:
        return("")
    return (str(weather.current.description) + " " + str(weather.current.temperature))


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
        while timer > 0:
            if end():
                break
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            if time is not current_time:
                time = current_time
                mem_write(current_time)
            sleep(1)
            timer -= 1
        timer = timer_max
        if end():
            break
        while timer > 0:
            if end():
                break
            now = loop.run_until_complete(asyncio.gather(getweather()))[0]
            if weather is not now:
                weather = now
                weather += "C"
                mem_write(weather)
            sleep(1)
            timer -= 1
        timer = timer_max
        if end():
            break
        while timer > 0:
            if end():
                break
            events = list(get_events(1))
            print(events[0])
            if events[0][0] == " ":
                mem_write(events[0][1])
            else:
                for i in events:
                    event_data = str(i[0]).split('-')
                    month_of_event = str(event_data[1])
                    day_of_event = str(event_data[2].split('T')[0])
                    name_of_event = str(i[1]).rstrip()
                    mem_write(month_of_event + "|" +
                              day_of_event + "|" + name_of_event)
            sleep(1)
            timer -= 1
        if end():
            break
