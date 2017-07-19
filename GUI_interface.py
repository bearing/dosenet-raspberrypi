#!/usr/bin/env/python

from appJar import gui
import Tkinter
import weather_DAQ
import air_quality_DAQ
import adc_DAQ

app = gui("Adafruit Weather Sensor", "800x400")

wdaq = weather_DAQ.weather_DAQ()
aqdaq = air_quality_DAQ.air_quality_DAQ()
adcdaq = adc_DAQ.adc_DAQ()

def weather_test(btn):
    wdaq.create_file()
    top = Tkinter.Tk()
    def start():
        global job1
        wdaq.start()
        job1=top.after(1000,start)
    def stop():
        global job1
        top.after_cancel(job1)
    
    startButton = Tkinter.Button(top, height=2, width=20, text ="Start", command = start)
    stopButton = Tkinter.Button(top, height=2, width=20, text ="Stop", command = stop)

    startButton.pack()
    stopButton.pack()

    top.mainloop()

def air_quality_test(btn):
    aqdaq.create_file()
    top = Tkinter.Tk()
    def start():
        global job2
        aqdaq.start()
        job2=top.after(1000,start)
    def stop():
        global job2
        top.after_cancel(job2)

    startButton = Tkinter.Button(top, height=2, width=20, text ="Start", command = start)
    stopButton = Tkinter.Button(top, height=2, width=20, text ="Stop", command = stop)

    startButton.pack()
    stopButton.pack()

    top.mainloop()

def CO2_test(btn):
    adcdaq.create_file()
    top = Tkinter.Tk()
    def start():
        global job3
        adcdaq.start()
        job3=top.after(1000,start)
    def stop():
        global job3
        top.after_cancel(job3)
    
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
app.addButton("Record Air Quality Data", air_quality_test)
app.setButtonWidth("Record Air Quality Data", "30")
app.setButtonHeight("Record Air Quality Data","4")
app.addButton("Record CO2 Data", CO2_test)
app.setButtonWidth("Record CO2 Data", "30")
app.setButtonHeight("Record CO2 Data","4")
app.addButton("Plot Weather Data",weather_plot)
app.setButtonWidth("Plot Weather Data","30")
app.setButtonHeight("Plot Weather Data","4")
app.setButtonFont("20",font="Helvetica")
app.go()
