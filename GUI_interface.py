
#!/usr/bin/env/python
import Tkinter
import os
import multiprocessing
import weather_DAQ
import air_quality_DAQ
import adc_DAQ
'''
import plot_manager_D3S
'''
# pressure, temp, humidity, co2, air, spectra, waterfall
plot_jobs = [None, None, None, None, None, None, None]

def close(index):
    if index == 0:
        wdaq.close(3)
    if index == 1:
        wdaq.close(1)
    if index == 2:
        wdaq.close(2)
    if index == 3:
        adcdaq.close(1)
    if index == 4:
        aqdaq.close(1)
'''
    if index == 5:
        mgrD3S.close()
    if index == 6:
        mgrD3S.close()
'''


wdaq = weather_DAQ.weather_DAQ()
aqdaq = air_quality_DAQ.air_quality_DAQ()
adcdaq = adc_DAQ.adc_DAQ()
'''
mgrD3S = plot_manager_D3S.Manager_D3S()
'''

top = Tkinter.Tk()
varAir = Tkinter.BooleanVar()
varAir.set(True)
vard3s = Tkinter.BooleanVar()
vard3s.set(True)
varCO2 = Tkinter.BooleanVar()
varCO2.set(True)
varWeather = Tkinter.BooleanVar()
varWeather.set(True)
'''
def start_D3S():
    try:
        mgrD3S.run()
    except:
        print("Error: Failed to start D3S")
'''    

def make_run_gui():
    top1 = Tkinter.Tk()
    global job1
    '''
    global job1
    global jobpress
    global jobhumid
    global jobtemp
    global jobco2
    global jobaq
    global jobd3s
    job1 = None
    jobpress = None
    jobtemp = None
    jobhumid = None
    jobco2 = None
    jobaq = None
    jobd3s = None
    plot_jobs[0] = jobpress
    plot_jobs[1] = jobtemp
    plot_jobs[2] = jobhumid
    plot_jobs[3] = jobco2
    plot_jobs[4] = jobaq
    '''
    
    def check_plots(index):
        global plot_jobs
        for i in range(len(plot_jobs)):
            if plot_jobs[i] is not None:
                if i != index:
                    #cancel job, close graph
                    top1.after_cancel(plot_jobs[i])
                    plot_jobs[i] = None
                    close(i)

    def start():
        
        global job1
        global jobd3s
        
        '''
        if vard3s.get():
            if jobd3s is None:
                jobd3s = multiprocessing.Process(target=start_D3S, args=()) 
        '''
        if varWeather.get(): 
            wdaq.start()
        if varAir.get():
            aqdaq.start()
        if varCO2.get():
            adcdaq.start()
        job1=top1.after(1000,start)

    def stop():
        global job1
        top1.after_cancel(job1)

    def press():
        
        global jobpress
        global jobhumid
        global jobtemp
        global jobco2 
        global jobaq 
        
        if jobhumid is not None:
            top1.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
        if jobtemp is not None:
            top1.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        if jobco2 is not None:
            top1.after_cancel(jobco2)
            jobco2 = None
            adcdaq.close(1)
        if jobaq is not None:
            top1.after_cancel(jobaq)
            jobaq = None
            aqdaq.close(1)
        wdaq.press()
        jobpress=top1.after(1000,press)
        
    def temp():
        global jobpress
        global jobhumid
        global jobtemp
        global jobco2
        global jobaq
        if jobhumid is not None:
            top1.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
        if jobpress is not None:
            top1.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        if jobco2 is not None:
            top1.after_cancel(jobco2)
            jobco2 = None
            adcdaq.close(1)
        if jobaq is not None:
            top1.after_cancel(jobaq)
            jobaq = None
            aqdaq.close(1)
        wdaq.temp()
        jobtemp=top1.after(1000,temp)
        
    def humid():
        global jobpress
        global jobhumid
        global jobtemp
        global jobco2
        global jobaq
        if jobpress is not None:
            top1.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        if jobtemp is not None:
            top1.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        if jobco2 is not None:
            top1.after_cancel(jobco2)
            jobco2 = None
            adcdaq.close(1)
        if jobaq is not None:
            top1.after_cancel(jobaq)
            jobaq = None
            aqdaq.close(1)
        wdaq.humid()
        jobhumid=top1.after(1000,humid)
        
    def CO2():
        '''
        global jobpress
        global jobhumid
        global jobtemp
        
        '''
        global plot_jobs
        '''
        if jobpress is not None:
            top1.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        if jobtemp is not None:
            top1.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        if jobaq is not None:
            top1.after_cancel(jobco2)
            jobaq = None
            aqdaq.close(1)
        if jobhumid is not None:
            top1.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
            '''
        check_plots(3)
        adcdaq.plot_CO2()
        plot_jobs[3]=top1.after(1000,CO2)
        
    def airquality():
        '''
        global jobpress
        global jobhumid
        global jobtemp
        global jobco2
        '''
        global plot_jobs
        '''
        if jobpress is not None:
            top1.after_cancel(jobpress)
            jobpress = None
            wdaq.close(3)
        if jobtemp is not None:
            top1.after_cancel(jobtemp)
            jobtemp = None
            wdaq.close(1)
        if jobco2 is not None:
            top1.after_cancel(jobco2)
            jobco2 = None
            adcdaq.close(1)
        if jobhumid is not None:
            top1.after_cancel(jobhumid)
            jobhumid = None
            wdaq.close(2)
            '''
        check_plots(4)
        aqdaq.pmplot()
        plot_jobs[4]=top1.after(1000,airquality)


    startButton1 = Tkinter.Button(top1, height=2, width=20, text ="Start", command = start)
    stopButton1 = Tkinter.Button(top1, height=2, width=20, text ="Stop", command = stop)
    startButton1.pack()
    stopButton1.pack()

    if varWeather.get():
        PressureButton = Tkinter.Button(top1, height=2, width=20, text = "Pressure", command = press)
        PressureButton.pack()
        TempButton = Tkinter.Button(top1, height=2, width=20, text = "Temperature", command = temp)
        TempButton.pack()
        HumidButton = Tkinter.Button(top1, height=2, width=20, text = "Humidity", command = humid)
        HumidButton.pack()

    if varCO2.get():
        CO2Button = Tkinter.Button(top1, height=2, width=20, text = "CO2", command = CO2)
        CO2Button.pack()
        
    if varAir.get():
        AirButton = Tkinter.Button(top1, height=2, width=20, text = "Air Quality", command = airquality)
        AirButton.pack()
    '''        
    if vard3s.get():
        d3sButton_spectra = TKinter.Button(top1, height=2, width=20, text = "D3S Spectra", command = D3S_spectra )
        d3sButton.pack()
        d3sButton_waterfall = Tkinter.Button(top1, height=2, width=20, text = "D3S Waterfall", command = D3S_waterfall)
        d3sButton_waterfall.pack()
        '''
    
    top1.attributes("-topmost", True)
    top1.mainloop()

def weather_test():
    if varCO2.get(): 
        print("create CO2 file")
        adcdaq.create_file()
    if varAir.get(): 
        print("create Air file")
        aqdaq.create_file()
    if varWeather.get(): 
        print("create weather file")
        wdaq.create_file()

    make_run_gui() 
  

AirButton = Tkinter.Checkbutton(top, text="Air Quality", variable=varAir)     
WeatherButton = Tkinter.Checkbutton(top, text='Weather Sensor', variable=varWeather)
CO2Button = Tkinter.Checkbutton(top, text="CO2 Sensor", variable=varCO2)
d3sButton = Tkinter.Checkbutton(top, text="D3S", variable=vard3s)
RecordButton = Tkinter.Button(top, text="Record Data", height=2, width=20, command = weather_test)  

AirButton.pack()   
WeatherButton.pack()
CO2Button.pack()
d3sButton.pack()
RecordButton.pack()
    
top.mainloop()
