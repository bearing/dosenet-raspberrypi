import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import deque
import serial
import sys
sys.stdout.flush()


class adc_DAQ(object):
    def __init__(self, maxdata, n_merge):
        self.time_queue=deque()
        self.n_merge=int(n_merge)
        self.count_list=[]
        self.time_list=[]
        self.maxdata=int(maxdata)
        self.count_queue=deque()
        self.count_error=deque()
        self.merge_test=False
        self.first_data = True
        self.last_time = None
        self.port = None
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
        metadata.append("Counts")
        #metadata.append("UV")
        adc_results.writerow(metadata[:])

    def start(self):
        global results
        date_time = datetime.datetime.now()    

    
        # Read all the ADC channel values in a list.
        values = [0]*8
        try:
            count = . . .
            self.merge_test=False
            self.add_data(self.count_queue,self.count_error,self.count_list,count)
            #self.add_data(self.UV_queue,self.UV_list,uv_index)
            self.add_time(self.time_queue, self.time_list, date_time)
            #print(self.time_queue[-1])
                          
            if self.merge_test==True:
                self.count_list=[]
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
                    #print(self.last_time)
                    if self.time_queue[-1] != self.last_time:
                        data = []
                        data.append(self.time_queue[-1])
                        data.append(self.count_queue[-1])
                        data.append(self.count_error[-1])
                        results.writerow(data)

                        self.last_time = self.time_queue[-1]
                    #else:
                        #print('duplicated data.')

                except IndexError:
                    #print('No new data being written.')
                    pass
            #else: 
                #print('No data acquired yet.')

                        
        except Exception as e:
            #print(e)
            #print("CO2 sensor error\n\n")
            pass


    # def plot_pg(self):
    #     if len(self.time_queue)>0:
    #         self.update_plot(1,self.time_queue,self.count_queue,self.count_error,"Time","CO2 Concentration (ppm)","CO2 Concentration vs. time")    

    

    def add_data(self, queue,queue_error, temp_list, data):
        datalist.append(data)
        if len(datalist)>=self.n_merge:
            queue.append(np.mean(np.asarray(datalist)))
            if queue_error is not None:
                queue_error.append(np.std(np.asarray(datalist)))
            datalist = []
        if len(queue)>self.maxdata:
            queue.popleft()

    # def update_plot(self,plot_id,xdata,ydata,yerr,xlabel,ylabel,title):
    #     plt.ion()
    #     fig = plt.figure(plot_id)
    #     plt.clf()
    #     #ax=fig.add_subplot(111)


    #     gs = GridSpec(6,1)
    #     ax1 = fig.add_subplot(gs[0,:])
    #     ax2 = fig.add_subplot(gs[1:5,:])


    #     ax1.set_axis_off()
    #     display = ydata[-1]
    #     sd = np.std(np.asarray(ydata))
    #     mean = np.mean(np.asarray(ydata))
    #     print("Display:{}+/-{}".format(mean,sd))
    #     if display <= 400:
    #         ax1.text(0.5, 1.2,"CO2 Concentration: "+ str(display), fontsize = 14 , ha = "center", backgroundcolor = "lightgreen")
    #         if sd<25:
    #         	ax2.set_ylim(mean-100,mean+100)
    #         else:
    #         	ax2.set_ylim(mean-4*sd,mean+4*sd)

    #     elif display > 400 and display <= 600:
    #         ax1.text(0.5, 1.2,"CO2 Concentration: "+str(display), fontsize = 14, ha = "center", backgroundcolor = "yellow")
    #         if sd<25:
    #         	ax2.set_ylim(mean-100,mean+100)
    #         else:
    #         	ax2.set_ylim(mean-4*sd,mean+4*sd)
    #     elif display > 600 and display <= 1000:
    #         ax1.text(0.5, 1.2,"CO2 Concentration: "+str(display), fontsize = 14, ha = "center", backgroundcolor = "orange")
    #         if sd<25:
    #         	ax2.set_ylim(mean-100,mean+100)
    #         else:
    #         	ax2.set_ylim(mean-4*sd,mean+4*sd)

    #     elif display > 1000:
    #         ax1.text(0.5, 1.2,"CO2 Concentration: "+str(display), fontsize = 14, ha = "center" , backgroundcolor = "red")
    #         if sd<25:
    #         	ax2.set_ylim(mean-100,mean+100)
    #         else:
    #         	ax2.set_ylim(mean-4*sd,mean+4*sd)



    #     ax2.set(xlabel = xlabel, ylabel = ylabel, title = title)

    #     ax2.plot(xdata,ydata,"r.-")
    #     ax2.errorbar(xdata, ydata, yerr=yerr, fmt='o')
    #     #fig.autofmt_xdate()
    #     ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    #     plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    #     fig.show()
    #     plt.pause(0.0005)    

    def add_time(self, queue, timelist, data):
        timelist.append(data)
        if len(timelist)>=self.n_merge:
            self.merge_test=True
            queue.append(timelist[int((self.n_merge)/2)])
        if len(queue)>self.maxdata:
            queue.popleft()    

    def close(self,plot_id):
         plt.close(plot_id)
