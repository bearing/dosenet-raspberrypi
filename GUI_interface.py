#!/usr/bin/env/python
'''
from appJar import gui
import weather_DAQ

app = gui("Adafruit Weather Sensor", "800x400")

wdaq = weather_DAQ.weather_DAQ()

global job1
global jobpress
global jobhumid
global jobtemp
job1 = None
jobpress = None
jobhumid = None
jobtemp = None

def weather_test(btn):
    wdaq.create_file()
    import Tkinter
    top = Tkinter.Tk()

    
    varWeather = Tkinter.IntVar()
    varCO2 = Tkinter.IntVar()
    def start():
        global job1
        if varWeather.get() == 1:
            wdaq.start()
        if varCO2.get() == 1:
            

    def start():
        global job1
        wdaq.start()   
        job1=top.after(1000,start)
    def stop():
        global job1
        top.after_cancel(job1)
    def press():
        global jobpress
        global jobhumid
        global jobtemp
        if jobhumid is not None:
            top.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
        if jobtemp is not None:
            top.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        wdaq.press()
        jobpress=top.after(1000,press)
        
    def temp():
        global jobpress
        global jobhumid
        global jobtemp
        if jobhumid is not None:
            top.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
        if jobpress is not None:
            top.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        wdaq.temp()
        jobtemp=top.after(1000,temp)
        
    def humid():
        global jobpress
        global jobhumid
        global jobtemp
        if jobpress is not None:
            top.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        if jobtemp is not None:
            top.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        wdaq.humid()
        jobhumid=top.after(1000,humid)
     

         
    WeatherButton = Tkinter.Checkbutton(top, text='Weather Sensor', variable=varWeather)
    CO2Button = Tkinter.Checkbutton(top, text="CO2 Sensor", variable=varCO2)  
    
    
    
    startButton = Tkinter.Button(top, height=2, width=20, text ="Start", command = start)
    stopButton = Tkinter.Button(top, height=2, width=20, text ="Stop", command = stop)
    PressureButton = Tkinter.Button(top, height=2, width=20, text = "Pressure", command = press)
    TempButton = Tkinter.Button(top, height=2, width=20, text = "Temperature", command = temp)
    HumidButton = Tkinter.Button(top, height=2, width=20, text = "Humidity", command = humid)
    
    WeatherButton.pack()
    CO2Button.pack()
    
    startButton.pack()
    stopButton.pack()
    PressureButton.pack()
    TempButton.pack()
    HumidButton.pack()

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

'''

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
    varWeather = Tkinter.IntVar()
    varCO2 = Tkinter.IntVar()
    varAir = Tkinter.IntVar()
    def start():
        global job1
        if varWeather.get() == 1:
            wdaq.start()
        if varCO2.get() == 1:
            adcdaq.start()
        if varAir.get() == 1:
            aqdaq.start()   
        job1=top.after(1000,start)
    def stop():
        global job1
        top.after_cancel(job1)
    def press():
        global jobpress
        global jobhumid
        global jobtemp
        if jobhumid is not None:
            top.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
        if jobtemp is not None:
            top.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        wdaq.press()
        jobpress=top.after(1000,press)
        
    def temp():
        global jobpress
        global jobhumid
        global jobtemp
        if jobhumid is not None:
            top.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
        if jobpress is not None:
            top.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        wdaq.temp()
        jobtemp=top.after(1000,temp)
        
    def humid():
        global jobpress
        global jobhumid
        global jobtemp
        if jobpress is not None:
            top.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        if jobtemp is not None:
            top.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        wdaq.humid()
        jobhumid=top.after(1000,humid)
     

         
    WeatherButton = Tkinter.Checkbutton(top, text='Weather Sensor', variable=varWeather)
    CO2Button = Tkinter.Checkbutton(top, text="CO2 Sensor", variable=varCO2)  
    AirButton = Tkinter.Checkbutton(top, text="Air Qualiy Sensor", variable=varAir)  
    startButton = Tkinter.Button(top, height=2, width=20, text ="Start", command = start)
    stopButton = Tkinter.Button(top, height=2, width=20, text ="Stop", command = stop)
    PressureButton = Tkinter.Button(top, height=2, width=20, text = "Pressure", command = press)
    TempButton = Tkinter.Button(top, height=2, width=20, text = "Temperature", command = temp)
    HumidButton = Tkinter.Button(top, height=2, width=20, text = "Humidity", command = humid)
    
    WeatherButton.pack()
    CO2Button.pack()
    AirButton.pack()
    startButton.pack()
    stopButton.pack()
    PressureButton.pack()
    TempButton.pack()
    HumidButton.pack()

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
