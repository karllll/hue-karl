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
    if transitiontime == -1:
        return 1
    else:
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

foundDefaultCount = 0
firstDefaultStateTime = 0
bulb1UnavailCount = 0
bulb2UnavailCount = 0
bulb3UnavailCount = 0
bulb4UnavailCount = 0
bulb5UnavailCount = 0


def zeroBools():
    eveBool = 0
    lateEveBool = 0
    morningToAfternoonBool = 0
    daytimeBool = 0
#every 10s
#Get Current Time / date

def defaultLightPhase(foundDefaultCount):
    #if one, phase red, then continue. If 2, then phase white, 
    if foundDefaultCount == 1:
        for light in api.lights:
            if light.state.hue == 8417:
                light.set_state({'hue': 8418, 'sat': 140, 'transitiontime': 1})

    elif foundDefaultCount > 1:
        phase(-1)
        phase(20)
    

while (True):    
    time = datetime.now()
    currentHour = time.hour
    sr = sun.get_local_sunrise_time(local_time_zone=denver).replace(tzinfo=None)
    ss = sunset()
    ssOffset = (ss - time).seconds
    srOffset = (sr - time).seconds
    #CHECK DEFAULTS
     
    for light in api.fetch_lights():
        if light.state.hue == 8417 and light.state.saturation == 140: #the manufacturer default color
            #If it's the same poll as another light, don't increment the counter.

            #   light.set_state({'hue': 8418, 'sat': 140, 'transitiontime': 1})
            if firstDefaultStateTime == 0:
                firstDefaultStateTime = time
             #   light.set_state({'hue': 8418, 'sat': 140, 'transitiontime': 1})
                foundDefaultCount = 1
                print("first default light")
            elif (time - firstDefaultStateTime).seconds > 30: #start counting again after X seconds
                firstDefaultStateTime = time
                foundDefaultCount = 1

            elif (time - firstDefaultStateTime).seconds == 0: #if it's the same second, just return
                print("Same second of default lights - not phasing.")
            elif (time - firstDefaultStateTime).seconds < 30:
                foundDefaultCount += 1
                print("Success! Incremented")
            

            print("Current counter:" + str(foundDefaultCount))
            defaultLightPhase(foundDefaultCount)
            





    #pdb.set_trace()
    #if a light is at it's default value (e.g., was turned on and off for a task) - pause some time (5m?), and then revert to the program at hand.

#sunset and sunrise lighting function happens 30min prior to action
    if  (srOffset / 60) < 30 and sunAboutToSet == 0 and (time - ss).days > -1:
        #The Sun is about to Set
        sunAboutToSet = 1
        #Execute Sunset Protocol

    if ((time - sr).seconds / 60) < 30 and sunAboutToRise == 0 and (time - sr).days > -1:
        #The Sun is about to rise
        sunAboutToRise = 1
        #Execute Sunrise Protocol

#reset sunset and sunrise after they occur so they can happen again the next day
    if ((time - sr).seconds / 60) > 15 and (time - sr).days > -1: #IF the current time is 1.5 hours after the sunrise time)
        sunAboutToRise = 0

    if ((time - ss).seconds / 60) > 15 and (time - ss).days > -1: #If the current time is 1.5 hours after the sunset time
        sunAboutToSet = 0

    #What period of the day are we in? Use that to determine brightness levels
    #if we're not doing a sunset or a sunrise (half hour before and 90 minutes after)

    #How do we only send one brightness command?
    #Create Bools as switches 
    #Or
    #Read the current value of the lights and change them if they equal the previously set max value (relies on a single bulb value, or managing all bulb values)
    
    #Evening -> Sunrise
#    if sunAboutToRise == 0 and sunAboutToSet == 0: #only modify brightness controls when not performing a sunset or sunrise operation
#        if currentHour >= 21 or currentHour <=sr.hour:
#            #after 10pm until sunrise
#            if lateEveBool == 0:
#                zeroBools()
#                lateEveBool = 1
#                #set lateEve brightness
#                changeBrightness(50, 2, 0)
#
#        if currentHour >= (ss.hour + 1) and currentHour <=20: #ss - 8pm
#            if eveBool == 0:
#                zeroBools()
#                eveBool = 1
#                #set Eve brightness
#                changeBrightness(200, 2, 0)
#
#        if currentHour > sr.hour and currentHour < ss.hour and daytimeBool == 0: #daytime - between sunrise and sunset
#            zeroBools()
#            daytimeBool = 1
#            changeBrightness(20, 2, 0)
#            #api.turn_off()
#        
#    if daytimeBool == 1 or eveBool == 1 or lateEveBool == 1:
#        if lastPhased == 0: #first run
#            lastPhased = time
#            phase(-1)
#            #phase(phaseMinutes) #sending the second command may override the first and cause the phase to take 20m intead of 1
#
#        elif ((time - lastPhased).seconds / 60) >= phaseMinutes:
#            lastPhased = time
#            phase(phaseMinutes)

    
    print("Sleeping.")
    sleep(2)
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

