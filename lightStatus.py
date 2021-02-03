import pdb
import time, random
from time import sleep
import datetime
from datetime import datetime, timedelta
from dateutil import tz
from suntime import Sun, SunTimeException
from hue_api import HueApi
#from .hue_api import HueApi

latitude = 39.74
longitude = -105.21 
lastPhased = 0
phaseMinutes = 20 #Transition time for phasing, also how long before phasing again

def sunset():
    sun = Sun(latitude, longitude)
    ss = sun.get_local_sunset_time(local_time_zone=denver)
    sr = sun.get_local_sunrise_time(local_time_zone=denver)
    if ss < sr:
        ss = ss + timedelta(1)
    return ss.replace(tzinfo=None)

def changeBrightness(brightness, transitiontime, jitter):
    #future feature: jitter on brightness, based on random value for each bulb
    transitiontime = transitiontimeMinutes(transitiontime)
    if brightness == 0:
        api.turn_off()
        return

    api.turn_on()
    bulb1bri = brightness
    bulb2bri = brightness + 70
    bulb3bri = brightness - 20
    api.lights[0].set_state({'bri': bulb1bri, 'transitiontime': transitiontime})
    api.lights[1].set_state({'bri': bulb2bri, 'transitiontime': transitiontime})
    api.lights[2].set_state({'bri': bulb3bri, 'transitiontime': transitiontime})
    api.lights[3].set_state({'bri': bulb2bri, 'transitiontime' : transitiontime})
    api.lights[4].set_state({'bri': bulb2bri, 'transitiontime' : transitiontime})

def transitiontimeMinutes(transitiontime):
    return transitiontime * 60 * 10

def phase(transitiontime): #if transition time is -1, phase immediately
    #    api.turn_on() #don't turn on lights - leave this up to manual control except for specific events.
    #Pick a random color value
    bulb1 = random.randint(0,65535)
    bulb2 = bulb1 + 5000
    bulb3 = bulb1 - 5000
    bulb4 = bulb2
    bulb5 = bulb2
    #if transitiontime is -1, phase immediately
    if transitiontime == -1:
        transitiontime = 1
    else:
        transitiontime = transitiontimeMinutes(transitiontime)
        
    if bulb2 > 65535:
        bulb2 = bulb2 - 65535
        bulb4 = bulb2
        bulb5 = bulb2
    if bulb3 < 0:
        bulb3 = 65535 + bulb3

    #api.lights[0].set_color(bulb1,255)
    #api.lights[1].set_color(bulb2,255)
    #api.lights[2].set_color(bulb3,255)
    api.lights[0].set_state({'hue': bulb1, 'sat': 255, 'transitiontime': transitiontime}) #20 minutes * 60 sec/min * 10 100ms/s 
    api.lights[1].set_state({'hue': bulb2, 'sat': 255, 'transitiontime': transitiontime}) #20 minutes * 60 sec/min * 10 100ms/s
    api.lights[2].set_state({'hue': bulb3, 'sat': 255, 'transitiontime': transitiontime}) #20 minutes * 60 sec/min * 10 100ms/s
    api.lights[3].set_state({'hue': bulb4, 'sat': 255, 'transitiontime': transitiontime}) #20 minutes * 60 sec/min * 10 100ms/s
    api.lights[4].set_state({'hue': bulb5, 'sat': 255, 'transitiontime': transitiontime}) #20 minutes * 60 sec/min * 10 100ms/s
    #transition time is number of seconds * 10, here it is 20 minutes


api = HueApi()
api.load_existing(cache_file='/home/pi/.apikey')
print("Key loaded")
sunAboutToSet = 0
sunAboutToRise = 0

#attempt immediate phasing for testing

sun = Sun(latitude,longitude)
denver = tz.gettz('America/Denver')
eveBool = 0
lateEveBool = 0
morningToAfternoonBool = 0
daytimeBool = 0

def zeroBools():
    eveBool = 0
    lateEveBool = 0
    morningToAfternoonBool = 0
    daytimeBool = 0
#every 10s
#Get Current Time / date
while (True):    
    time = datetime.now()
    currentHour = time.hour
    sr = sun.get_local_sunrise_time(local_time_zone=denver).replace(tzinfo=None)
    ss = sunset()
    ssOffset = (ss - time).seconds
    srOffset = (sr - time).seconds
    print ("Light\t\tBrightness\tHue\tSaturation")
    for light in api.fetch_lights():
        print(str(light) + "\t\t" + str(light.state.brightness) + "\t" + str(light.state.hue) + "\t" + str(light.state.saturation))
    
    #if a light is at it's default value (e.g., was turned on and off for a task) - pause some time (5m?), and then revert to the program at hand.

#sunset and sunrise lighting function happens 30min prior to action
    
#    pdb.set_trace()
    #Evening -> Sunrise
    sleep(5)
##Sunrise (defined Colors)

##Sunset (defined colors)

    

#If time is more than an hour later than sunset, switch to randomized play.
#Pick Random color
#Pick +2 offsets
#Phase to new colors over an hour
##On 10s loop, compare to previous value of time
##If time >=1hr, repeat (rando generate new color, offsets, and phase to them over 1hr)

##Sunrise

#Dim as a function of sunset (Brightness as a function of time vs sunset and vs sunrise (what happens when we subtract 2am the next day from 12pm)

