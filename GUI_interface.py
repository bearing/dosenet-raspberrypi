
#!/usr/bin/env/python
import Tkinter
from Tkinter import Entry, StringVar, Label
import weather_DAQ
import air_quality_DAQ
import adc_DAQ
import plot_manager_D3S
import threading
import os

# pressure, temp, humidity, co2, air, spectra, waterfall
plot_jobs = [None, None, None, None, None, None, None]

def close(index):
    global wdaq
    global adcdaq
    global mgrD3S
    global aqdaq
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
    if index == 5:
        mgrD3S.close(2)
    if index == 6:
        mgrD3S.close(1)

option1 = [5,10,15,20,25,30,35,40,45,50]
option2 = [1,2,3,4,5,10,20,30,40,50,60,120,180,240,300]

top = Tkinter.Tk()
top.geometry("800x400")
varAir = Tkinter.BooleanVar()
vard3s = Tkinter.BooleanVar()
varCO2 = Tkinter.BooleanVar()
varWeather = Tkinter.BooleanVar()
maxdata = Tkinter.StringVar()
maxdata.set(option1[3])
n_merge = Tkinter.StringVar()
n_merge.set(option2[2])



def make_run_gui():
    top1 = Tkinter.Tk()
    top1.geometry('+0+410')
    # top2 = Tkinter.Tk()
    # top2.geometry('+0+410')
    global jobCO2
    global jobAir
    global jobWeather
    global jobd3s
    jobd3s = None

    def check_plots(index):
        global plot_jobs
        for i in range(len(plot_jobs)):
            if plot_jobs[i] is not None:
                if i != index:
                    #cancel job, close graph
                    top1.after_cancel(plot_jobs[i])
                    plot_jobs[i] = None
                    close(i)

    def start_D3S():
        global mgrD3S
        if vard3s.get():
            mgrD3S.run()


    def start():
        global jobCO2
        global jobAir
        global jobWeather
        global jobd3s
        global wdaq
        global adcdaq
        global mgrD3S
        global aqdaq
        if jobd3s is None:
            jobd3s = threading.Thread(target=start_D3S, args=())
            try:
                jobd3s.start()
            except:
                print("Error: Failed to start D3S")
        if varWeather.get():
            wdaq.start()
            jobWeather =top1.after(1000,start)
        if varAir.get():
            aqdaq.start()
            jobAir =top1.after(1000,start)
        if varCO2.get():
            adcdaq.start()
            jobCO2=top1.after(250,start)

    def stop():
        global jobCO2
        global jobAir
        global jobWeather
        global jobd3s
        global wdaq
        global adcdaq
        global aqdaq

        if varWeather.get():
            weather_DAQ.close_file()
            top1.after_cancel(jobWeather)
        if varAir.get():
            aqdaq.close_file()
            top1.after_cancel(jobAir)
        if varCO2.get():
            adcdaq.close_file()
            top1.after_cancel(jobCO2)

        jobd3s = None
        check_plots(-1)
        if vard3s.get():
            global mgrD3S
            if jobd3s is not None:
                mgrD3S.takedown()
                print(mgrD3S.running)
            os.system("pkill -9 -f GUI_interface.py")


    def press():
        global wdaq
        global plot_jobs
        check_plots(0)
        wdaq.press()
        plot_jobs[0]=top1.after(int(n_merge.get())*1000,press)

    def temp():
        global wdaq
        global plot_jobs
        check_plots(1)
        wdaq.temp()
        plot_jobs[1]=top1.after(int(n_merge.get())*1000,temp)

    def humid():
        global wdaq
        global plot_jobs
        check_plots(2)
        wdaq.humid()
        plot_jobs[2]=top1.after(int(n_merge.get())*1000,humid)

    def CO2():
        global adcdaq
        global plot_jobs
        check_plots(3)
        adcdaq.plot_CO2()
        plot_jobs[3]=top1.after(int(n_merge.get())*1000,CO2)

    def airquality():
        global aqdaq
        global plot_jobs
        check_plots(4)
        aqdaq.pmplot()
        plot_jobs[4]=top1.after(int(n_merge.get())*1000,airquality)

    def D3S_spectra():
        global mgrD3S
        global plot_jobs
        check_plots(5)
        mgrD3S.plot_spectrum(2)
        print("Updating spectra")
        plot_jobs[5]=top1.after(int(n_merge.get())*1000,D3S_spectra)

    def D3S_waterfall():
        global mgrD3S
        global plot_jobs
        check_plots(6)
        mgrD3S.plot_waterfall(1)
        plot_jobs[6]=top1.after(int(n_merge.get())*1000,D3S_waterfall)


    startButton1 = Tkinter.Button(top1, height=2, width=10, text ="Start", command = start)
    stopButton1 = Tkinter.Button(top1, height=2, width=10, text ="Stop", command = stop)
    startButton1.grid(row=0, column=0)
    stopButton1.grid(row=0, column=1)

    if varWeather.get():
        PressureButton = Tkinter.Button(top1, height=2, width=10, text = "Pressure", command = press)
        PressureButton.grid(row=0, column=2)
        TempButton = Tkinter.Button(top1, height=2, width=10, text = "Temperature", command = temp)
        TempButton.grid(row=0, column=3)
        HumidButton = Tkinter.Button(top1, height=2, width=10, text = "Humidity", command = humid)
        HumidButton.grid(row=0, column=4)

    if varCO2.get():
        CO2Button = Tkinter.Button(top1, height=2, width=10, text = "CO2", command = CO2)
        CO2Button.grid(row=0, column=5)

    if varAir.get():
        AirButton = Tkinter.Button(top1, height=2, width=10, text = "Air Quality", command = airquality)
        AirButton.grid(row=0, column=6)

    if vard3s.get():
        d3sButton_spectra = Tkinter.Button(top1, height=2, width=10, text = "D3S Spectra", command = D3S_spectra )
        d3sButton_spectra.grid(row=0, column=7)
        d3sButton_waterfall = Tkinter.Button(top1, height=2, width=10, text = "D3S Waterfall", command = D3S_waterfall)
        d3sButton_waterfall.grid(row=0, column=8)

    #top2.attributes("-topmost", True)
    #top2.mainloop()
    top1.attributes("-topmost", True)
    top1.mainloop()

def weather_test():

    if varCO2.get():
        global adcdaq
        adcdaq = adc_DAQ.adc_DAQ(maxdata.get(), int(n_merge.get())*4)
        print("create CO2 file")
        adcdaq.create_file()
    if varAir.get():
        global aqdaq
        aqdaq = air_quality_DAQ.air_quality_DAQ(maxdata.get(), int(n_merge.get()))
        print("create Air file")
        aqdaq.create_file()
    if varWeather.get():
        global wdaq
        wdaq = weather_DAQ.weather_DAQ(maxdata.get(), int(n_merge.get()))
        print("create weather file")
        wdaq.create_file()
    if vard3s.get():
        global mgrD3S
        mgrD3S = plot_manager_D3S.Manager_D3S(int(n_merge.get()), int(maxdata.get()), plot = False)
        print("create D3S file")

    make_run_gui()


AirButton = Tkinter.Checkbutton(top, text="Air Quality", variable=varAir, font="Times 25")
WeatherButton = Tkinter.Checkbutton(top, text='Weather Sensor', variable=varWeather, font="Times 25")
CO2Button = Tkinter.Checkbutton(top, text="CO2 Sensor", variable=varCO2, font="Times 25")
d3sButton = Tkinter.Checkbutton(top, text="D3S", variable=vard3s, font="Times 25")
# maxdata = Entry(top)
# n_merge = Entry(top)
maxdata_option = Tkinter.OptionMenu(top, maxdata, *option1)
n_merge_option = Tkinter.OptionMenu(top, n_merge, *option2)

maxdata_text = Label(top, text = "Data points on plot", font = "Times 20")
nmerge_text = Label(top, text = 'Integration seconds (s)', font = "Times 20")
RecordButton = Tkinter.Button(top, text="Record Data", command = weather_test, font="Times 25")

AirButton.pack(pady = 3)
WeatherButton.pack(pady = 3)
CO2Button.pack(pady = 3)
d3sButton.pack(pady = 3)
maxdata_text.pack()
maxdata_option.pack()
nmerge_text.pack()
n_merge_option.pack()
RecordButton.pack(pady = 6)

top.mainloop()
