#!/usr/bin/env/python

from appJar import gui
import weather_DAQ

app = gui("Adafruit Weather Sensor", "800x400")

wdaq = weather_DAQ.weather_DAQ()

def weather_test(btn):
    wdaq.create_file()
    import Tkinter
    top = Tkinter.Tk()
    '''
    varWeather = Tkinter.IntVar()
    varCO2 = Tkinter.IntVar()
    def start():
        global job1
        if varWeather.get() == 1:
            wdaq.start()
        if varCO2.get() == 1:
            '''
    def start():
        global job1
        wdaq.start()   
        job1=top.after(1000,start)
    def stop():
        global job1
        top.after_cancel(job1)
    def press():
        global jobhumid
        global jobpress
        global jobtemp
        cancel()
        wdaq.press()
        jobpress=top.after(1000,press)
    def temp():
        global jobhumid
        global jobpress
        global jobtemp
        cancel()
        wdaq.temp()
        jobtemp=top.after(1000,temp)
    def humid():
        global jobhumid
        global jobpress
        global jobtemp
        cancel()
        wdaq.humid()
        jobhumid=top.after(1000,humid)
        
    def cancel():
        global jobhumid
        global jobpress
        global jobtemp
        if jobhumid is not None:
            top.after_cancel(jobhumid)
            jobhumid = None
        if jobpress is not None:
            top.after_cancel(jobpress)
            jobpress = None
        if jobtemp is not None:
            top.after_cancel(jobtemp)
            jobtemp = None
    '''     
    WeatherButton = Tkinter.Checkbutton(top, text='Weather Sensor', variable=varWeather)
    CO2Button = Tkinter.Checkbutton(top, text="CO2 Sensor", variable=varCO2)
    '''
    startButton = Tkinter.Button(top, height=2, width=20, text ="Start", command = start)
    stopButton = Tkinter.Button(top, height=2, width=20, text ="Stop", command = stop)
    PressureButton = Tkinter.Button(top, height=2, width=20, text = "Pressure", command = press)
    TempButton = Tkinter.Button(top, height=2, width=20, text = "Temperature", command = temp)
    HumidButton = Tkinter.Button(top, height=2, width=20, text = "Humidity", command = humid)
    '''
    WeatherButton.pack()
    CO2Button.pack()
    '''
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
