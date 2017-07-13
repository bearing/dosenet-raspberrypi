#!/usr/bin/env/python

from appJar import gui
import os
import matplotlib.pyplot as plt
import dateutil
import numpy as np
from matplotlib.dates import DateFormatter
import time
import datetime
import csv
import weather_DAQ

app = gui("Adafruit Weather Sensor", "800x400")
from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

wdaq = weather_DAQ.weather_DAQ()

def weather_test(btn):

    wdaq.open_file()
    wdaq.startstop()


def weather_plot(btn):
    
    app = gui("Record Weather Data","800x400")
    wdaq.set_widgets()
    wdaq.lists()
    app.addButton("OK",wdaq.plotdata())
    app.setButtonWidth("OK","20")
    app.setButtonHeight("OK","4")
    app.setButtonFont("20","Helvetica")
    app.go()
    

app.addButton("Record Weather Data", weather_test)
app.setButtonWidth("Record Weather Data", "30")
app.setButtonHeight("Record Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.addButton("Plot Weather Data",weather_plot)
app.setButtonWidth("Plot Weather Data","30")
app.setButtonHeight("Plot Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.go()
