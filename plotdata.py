# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 15:43:02 2017

@author: Ludi Cao
"""
import time
import datetime
import csv
import os
from appJar import gui
import numpy as np
import dateutil
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt

class plotdata(object):
    def __init__(self):
        self.times=[]
        self.times2=[]
        self.times3=[]
        self.degrees_list=[]
        self.pressure_list=[]
        self.humidity_list=[]
        self.temp_ave=[]
        self.temp_unc = []
        self.pressure_ave=[]
        self.pressure_unc=[]
        self.humidity_ave=[]
        self.humidity_unc=[]
        self.merge_times = []
        self.merge_times2 = []
        self.merge_times3 = []
    
    def plotdata1(self): 
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

    
        def ok(btn):
            import Tkinter
            top = Tkinter.Tk()
            n_merge=int(app.getEntry("n"))
            user_file=app.getOptionBox("Files")
            results = csv.reader(open(user_file), delimiter=',')          

                    
            def temp():
                ok.plotting(self.times, self.degrees_list, self.temp_ave, self.temp_unc, self.merge_times)
            
            def humid():
                ok.plotting(self.times2, self.humidity_list, self.humidity_ave, self.humidity_unc, self.merge_times2)
            
            def press():
                ok.plotting(self.times3, self.pressure_list, self.pressure_ave, self.pressure_unc, self.merge_times3)
            
            def plotting(self,timelist, datalist, listave, listunc, listmerge):
                row_counter=0              
                for r in results:
                    if row_counter>0:
                        timelist.append(dateutil.parser.parse(r[0]))
                        datalist.append(float(r[1]))                
                    row_counter+=1
             
                ndata = int(len(datalist))
                nsum_data = int(ndata/n_merge)
                
                for i in range(nsum_data):
                    itemp = datalist[i*n_merge:(i+1)*n_merge]
                    itemp_array = np.asarray(itemp)
                    temp_mean = np.mean(itemp_array)
                    temp_sigma = np.sqrt(np.var(itemp_array))
                    listave.append(temp_mean)
                    listunc.append(temp_sigma)
            
                for i in range(nsum_data):
                    itimes = timelist[i*n_merge:(i+1)*n_merge]
                    itime = itimes[int(len(itimes)/2)]
                    listmerge.append(itime)

                fig=plt.figure()
                ax=fig.add_subplot(111)   
                plt.plot(listmerge, listave, "b.")
                plt.errorbar(listmerge, listave, yerr = self.temp_unc)
                plt.title("Temperature")
                plt.xlabel("Time(s)")
                plt.ylabel("Temperature(C)")
                fig.autofmt_xdate()
                ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
                plt.show()
            

            tempButton = Tkinter.Button(top, height=2, width=20, text="Temperature PLot", command=temp)
            pressButton =Tkinter.Button(top, height=2, width=20, text="Pressure Plot", command=press)
            humidButton = Tkinter.Button(top, height=2, width=20, text="Humidity Plot", command=humid)
            
            tempButton.pack()
            pressButton.pack()
            humidButton.pack()
            
            top.mainloop()
            
        app.addButton("OK",ok)
        app.setButtonWidth("OK","20")
        app.setButtonHeight("OK","4")
        app.setButtonFont("20","Helvetica")
        app.go()
