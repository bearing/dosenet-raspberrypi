#!/usr/bin/env/python

from appJar import gui
import weather_DAQ
import datetime
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt

app = gui("Adafruit Weather Sensor", "800x400")
from Adafruit_BME280 import *

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

wdaq = weather_DAQ.weather_DAQ()


def weather_test(btn):
    wdaq.create_file()
    import Tkinter
    top = Tkinter.Tk()
    temp=[1,2]
    time=[3,4]
    date_time = datetime.datetime.now()
    degrees = sensor.read_temperature()
    plt.ion()
    fig = plt.figure(1)
    ax=fig.add_subplot(111)
    plt.xlabel("Time")
    plt.ylabel("Temperature(C)")
    plt.plot(time, temp,"r." )
    plt.show()
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    def start():
        global job1
        wdaq.create_file()
        wdaq.start()
        time.append(date_time)
        temp.append(degrees)
        plt.plot(time, temp,"r." )
        plt.pause(0.0005)
        plt.show()
        job1=top.after(1000,start)
    def stop():
        global job1
        top.after_cancel(job1)
    
    startButton = Tkinter.Button(top, height=2, width=20, text ="Start", command = start)
    stopButton = Tkinter.Button(top, height=2, width=20, text ="Stop", command = stop)

    startButton.pack()
    stopButton.pack()

    top.mainloop()

def weather_plot(btn):

    wdaq.plotdata()    

app.addButton("Record Weather Data", weather_test)
app.setButtonWidth("Record Weather Data", "30")
app.setButtonHeight("Record Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.addButton("Plot Weather Data",weather_plot)
app.setButtonWidth("Plot Weather Data","30")
app.setButtonHeight("Plot Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.go()
