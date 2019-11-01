import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import deque
from sensor import Sensor
import sys
sys.stdout.flush()


class pocket_geiger_DAQ(object):
    def __init__(self, maxdata, n_merge):
        self.time_queue=deque()
        self.n_merge=int(n_merge)
        self.count_list=[]
        self.error_list=[]
        self.time_list=[]
        self.maxdata=int(maxdata)
        self.count_queue=deque()
        self.count_error=deque()
        self.merge_test=False
        self.first_data = True
        self.last_time = None
        self.sensor = Sensor()
        print('N MERGE: {}'.format(n_merge) )

    def create_file(self):
    	import csv
        global results
        file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        id_info = []
        with open ('/home/pi/config/server_config.csv') as f:
        	reader = csv.reader(f)
        	for row in reader:
        		id_info.append(row)
        filename = "/home/pi/data/"+"_".join(row)+"_geiger_counter"+file_time+".csv"
        f = open(filename, "ab+")
        results=csv.writer(open(filename, "ab+"), delimiter = ",")
        metadata = []
        metadata.append("Date and Time")
        metadata.append("Count Rate")
        #metadata.append("UV")
        results.writerow(metadata[:])

    def start(self):
        global results
        date_time = time.time()

        try:
            count_cpm,count_err = self.sensor.get_cpm(date_time-120,date_time)
            print('CPM = {}+/-{}'.format(count_cpm,count_err))
            self.merge_test=False
            self.add_data(self.count_queue,self.count_error,
                          self.count_list,self.error_list,count_cpm,count_err)
            self.add_time(self.time_queue, self.time_list, date_time)

            if self.merge_test==True:
                self.count_list=[]
                self.error_list=[]
                #self.UV_list=[]
                self.time_list=[]
            if self.first_data and len(self.count_queue) != 0:
                for i in range(len(self.count_queue)):
                    data = []
                    data.append(self.time_queue[i])
                    data.append(self.count_queue[i])
                    data.append(self.count_error[i])
                    results.writerow(data)

                self.last_time = data[0]
                self.first_data = False
            elif not self.first_data:
                try:

                    if self.time_queue[-1] != self.last_time:
                        data = []
                        data.append(self.time_queue[-1])
                        data.append(self.count_queue[-1])
                        data.append(self.count_error[-1])
                        results.writerow(data)

                        self.last_time = self.time_queue[-1]

                except IndexError:
                    #print('No new data being written.')
                    pass

        except Exception as e:
            print(e)
            #print("CO2 sensor error\n\n")
            pass


    def plot_pg(self):
        if len(self.time_queue)>0:
            self.update_plot(1,self.time_queue,self.count_queue,self.count_error,"Time","Count Rate (CPM)","Count Rate (CPM) vs. time")



    def add_data(self, queue, queue_error, temp_list, error_list, data, error):
        temp_list.append(data)
        error_list.append(error)
        if len(temp_list)>=self.n_merge:
            queue.append(np.mean(np.asarray(temp_list)))
            if queue_error is not None:
                queue_error.append(np.mean(np.asarray(error_list)))
            temp_list = []
            error_list = []
        if len(queue)>self.maxdata:
            queue.popleft()
            queue_error.popleft()

    def update_plot(self,plot_id,xdata,ydata,yerr,xlabel,ylabel,title):
        plt.ion()
        fig = plt.figure(plot_id)
        plt.clf()
        #ax=fig.add_subplot(111)


        gs = GridSpec(6,1)
        ax1 = fig.add_subplot(gs[0,:])
        ax2 = fig.add_subplot(gs[1:5,:])


        ax1.set_axis_off()

        display = int(ydata[-1])
        dose = round(display*0.036,4)
        dose_display = str(dose) + " $\mu$Sv/hr"

        if display <= 150:
            ax1.text(0.1, 1.2,"CPM: "+ str(display), fontsize = 14 , ha = "center", backgroundcolor = "lightgreen")
            ax1.text(0.7, 1.2,"Dose: "+ dose_display, fontsize = 14, ha = "center", backgroundcolor = "lightgreen")

        elif display > 150 and display <= 500:
            ax1.text(0.1, 1.2,"CPM: "+str(display), fontsize = 14, ha = "center", backgroundcolor = "yellow")
            ax1.text(0.7, 1.2,"Dose: "+dose_display, fontsize = 14, ha = "center" , backgroundcolor = "yellow")


        elif display > 500 and display <= 2000:
            ax1.text(0.1, 1.2,"Counts: "+str(display), fontsize = 14, ha = "center", backgroundcolor = "orange")
            ax1.text(0.7, 1.2,"Dose: "+dose_display, fontsize = 14, ha = "center",  backgroundcolor = "orange")


        elif display > 2000:
            ax1.text(0.2, 1.2,"Counts: "+str(display), fontsize = 14, ha = "center" , backgroundcolor = "red")
            ax1.text(0.7, 1.2,"Dose: "+dose_display, fontsize = 14, ha = "center", backgroundcolor = "red")



        ax2.set(xlabel = xlabel, ylabel = ylabel, title = title)

        ax2.plot(xdata,ydata,"r.-")
        ax2.errorbar(xdata, ydata, yerr=yerr, fmt='o')
        #fig.autofmt_xdate()
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        fig.show()
        plt.pause(0.0005)

    def add_time(self, queue, timelist, data):
        timelist.append(data)
        if len(timelist)>=self.n_merge:
            self.merge_test=True
            queue.append(timelist[int((self.n_merge)/2)])
            timelist=[]
        if len(queue)>self.maxdata:
            queue.popleft()

    def close(self,plot_id):
         plt.close(plot_id)
