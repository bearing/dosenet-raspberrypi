# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 10:25:03 2017

@author: Ludi Cao
"""

from appJar import gui
import os


app = gui("Adafruit Weather Sensor", "800x400")
from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

def weather_test(btn):
    app=gui("Weather Test","800x400")
    def press1(btn):
        os.system('sudo bash /home/pi/dosenet-raspberrypi/python weather_test.py')
    def press2(btn):
        os.system('sudo bash /home/pi/dosenet-raspberrypi/python weather_test_stop py')
    app.addButton("Start",press1)
    app.setButtonWidth("Start","20")
    app.setButtonHeight("Start","4")
    app.setButtonFont("20","Helvetica")
    app.addButton("Stop",press2)
    app.setButtonWidth("Stop","20")
    app.setButtonHeigth("Stop","4")
    app.go()
    
def weather_plot(btn):
    app=gui("Weather Plot","800x400")
    app.addLabel("1","Please choose a following .csv file")
    file_name=[]
    for filename in os.listdir('.'):
        if filename.endswith(".csv"):
            file_name.append(os.path.join('.', filename))
            app.setFont(20)
            app.addOptionBox("Files",file_name)
            app.setOptionBoxHeight("Files","4")
            app.addLabel("2","Enter the number of data points to merge:")
            app.setLabelFont("20","Heletica")
            app.addNumericEntry("n")
            app.setFocus("n")
            app.setNumericEntryHeight("n","4")

app.addButton("Record Weather Data", weather_test)
app.setButtonWidth("Record Weather Data", "30")
app.setButtonHeight("Record Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.addButton("Plot Weather Data",weather_plot)
app.setButtonWidth("Plot Weather Data","30")
app.setButtonHeight("Plot Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.go()
