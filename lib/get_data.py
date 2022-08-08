from time import sleep
import ipc
import os
from datetime import datetime
import python_weather
import asyncio

from calander import get_events
from location import fill_json

async def getweather():
    client = python_weather.Client(format=python_weather.METRIC)

    weather = await client.find("Duvall, WA")

    await client.close()
    
    return (str(weather.current.sky_text) + " " + str(weather.current.temperature))



fill_json()
time = 0
weather = ""
loop = asyncio.get_event_loop()
timer_max = 10
while True:
    timer = timer_max
    while timer > 0:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        if time is not current_time:
            time = current_time
            ipc.mem_write(current_time)
        sleep(1)
        timer -= 1
    timer = timer_max
    # print("Switch")
    while timer > 0:
        now = loop.run_until_complete(asyncio.gather(getweather()))[0]
        if weather is not now:
            weather = now
            weather += "C"
            ipc.mem_write(weather)
        sleep(1)
        timer -= 1
    timer = timer_max
    # print("Switch 2")
    while timer > 0:
        for i in get_events():
            event_data = str(i[0]).split('-')
            month_of_event = str(event_data[1])
            day_of_event = str(event_data[2].split('T')[0])
            name_of_event = str(i[1]).rstrip()
            ipc.mem_write(month_of_event + "|" + day_of_event + "|" + name_of_event)
        sleep(1)
        timer -= 1
    
    # print("Switch 3")