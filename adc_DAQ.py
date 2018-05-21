import time
import datetime
import csv
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import deque
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import sys
import os
sys.stdout.flush()

CLK  = 18
MISO = 23
MOSI = 24
CS   = 25

class adc_DAQ(object):
    def __init__(self, maxdata, n_merge):
        self.time_queue=deque()
        self.n_merge=int(n_merge)
        self.CO2_list=[]
        self.UV_list=[]
        self.time_list=[]
        self.maxdata=int(maxdata)
        self.CO2_queue=deque()
        self.CO2_error=deque()
        self.UV_queue=deque()
        self.merge_test=False
        self.first_data = True
        self.last_time = None
        self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
        print('N MERGE: {}'.format(n_merge) )

    def create_file(self):
    	import csv
        global adc_file
        global adc_results
        file_time= time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        id_info = []
        with open ('/home/pi/config/server_config.csv') as f:
        	reader = csv.reader(f)
        	for row in reader:
        		id_info.append(row)
        filename = "/home/pi/data/"+"_".join(row)+"_CO2"+file_time+".csv"
        adc_file = open(filename, "ab+")
        adc_results=csv.writer(adc_file, delimiter = ",")
        metadata = []
        metadata.append("Date and Time")
        metadata.append("CO2 (ppm)")
        #metadata.append("UV")
        adc_results.writerow(metadata[:])

    def start(self):
        global adc_file
        global adc_results
        date_time = datetime.datetime.now()
        self.mcp=Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

        # Read all the ADC channel values in a list.
        values = [0]*8
        try:
            for i in range(8):
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = self.mcp.read_adc(i)
            # Print the ADC values.
            # print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
            #print('| {0:>4} | {1:>4} |'.format(values[0],values[7]))
            concentration = 5000/496*values[0] - 1250
            #print("|{}|\n".format(concentration))
            # Pause for half a second.
            #uv_index = values[7]
            results = []
            results.append(date_time)
            results.append(concentration)
            #results.append(uv_index)

            #adc_results.writerow(results[:])

            self.merge_test=False
            self.add_data(self.CO2_queue,self.CO2_error,self.CO2_list,concentration)
            #self.add_data(self.UV_queue,self.UV_list,uv_index)
            self.add_time(self.time_queue, self.time_list, date_time)
            #print(self.time_queue[-1])

            if self.merge_test==True:
                self.CO2_list=[]
                #self.UV_list=[]
                self.time_list=[]
            if self.first_data and len(self.CO2_queue) != 0:
                for i in range(len(self.CO2_queue)):
                    data = []
                    data.append(self.time_queue[i])
                    data.append(self.CO2_queue[i])
                    data.append(self.CO2_error[i])
                    adc_results.writerow(data)
                    adc_file.flush()

                self.last_time = data[0]
                self.first_data = False
            elif not self.first_data:
                try:
                    #print(self.last_time)
                    if self.time_queue[-1] != self.last_time:
                        data = []
                        data.append(self.time_queue[-1])
                        data.append(self.CO2_queue[-1])
                        data.append(self.CO2_error[-1])
                        adc_results.writerow(data)
                        adc_file.flush()

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


    def plot_CO2(self):
        if len(self.time_queue)>0:
            self.update_plot(1,self.time_queue,self.CO2_queue,self.CO2_error,"Time","CO2 Concentration (ppm)","CO2 Concentration vs. time")

    def plot_UV(self):
        if len(self.time_queue)>0:
            self.update_plot(2,self.time_queue,self.UV_queue,"Time","UV Index","UV vs.time")

    def add_data(self, queue,queue_error, temp_list, data):
        temp_list.append(data)
        if len(temp_list)>=self.n_merge:
        	temp_list = np.asarray(temp_list)
        	print(temp_list)
        	pre_mean = np.mean(temp_list)
        	pre_sd = np.std(temp_list)
        	print(pre_mean,pre_sd)
        	while pre_sd > 15.0:
        		temp_list = temp_list[np.logical_and(temp_list<(pre_mean+pre_sd), temp_list>(pre_mean-pre_sd))]
        		print(temp_list)
        		pre_mean = np.mean(temp_list)
        		pre_sd = np.std(temp_list)
        		print(pre_mean,pre_sd)

        	queue.append(np.mean(temp_list))
        	queue_error.append(np.std(temp_list))
        	#print(queue)
        # print(temp_list)
        # print('MEAN:{}'.format(np.mean(np.asarray(temp_list))))
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
        display = ydata[-1]
        sd = np.std(np.asarray(ydata))
        mean = np.mean(np.asarray(ydata))
        print("Display:{}+/-{}".format(mean,sd))
        display_text = "CO2 Concentration: "+ str(display)+" (ppm)"
        if display <= 400:
            ax1.text(0.5, 1.2,display_text, fontsize = 14 , ha = "center", backgroundcolor = "lightgreen")
            if sd<25:
            	ax2.set_ylim(mean-100,mean+100)
            else:
            	ax2.set_ylim(mean-4*sd,mean+4*sd)

        elif display > 400 and display <= 600:
            ax1.text(0.5, 1.2,display_text, fontsize = 14, ha = "center", backgroundcolor = "yellow")
            if sd<25:
            	ax2.set_ylim(mean-100,mean+100)
            else:
            	ax2.set_ylim(mean-4*sd,mean+4*sd)
        elif display > 600 and display <= 1000:
            ax1.text(0.5, 1.2,display_text, fontsize = 14, ha = "center", backgroundcolor = "orange")
            if sd<25:
            	ax2.set_ylim(mean-100,mean+100)
            else:
            	ax2.set_ylim(mean-4*sd,mean+4*sd)

        elif display > 1000:
            ax1.text(0.5, 1.2,display_text, fontsize = 14, ha = "center" , backgroundcolor = "red")
            if sd<25:
            	ax2.set_ylim(mean-100,mean+100)
            else:
            	ax2.set_ylim(mean-4*sd,mean+4*sd)



        ax2.set(xlabel = xlabel, ylabel = ylabel, title = title)

        ax2.plot(xdata,ydata,"r.-")
        ax2.errorbar(xdata, ydata, yerr=yerr, fmt='o')
        #fig.autofmt_xdate()
        ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        fig.show()
        plt.pause(0.0005)

    def add_time(self, queue, timelist, data):
        timelist.append(data)
        if len(timelist)>=self.n_merge:
            self.merge_test=True
            queue.append(timelist[int((self.n_merge)/2)])
        if len(queue)>self.maxdata:
            queue.popleft()

    def close_file(self):
        global adc_file
        sys_cmd = 'scp {} pi@192.168.4.1:/home/pi/data'.format(adc_file.name)
        print(sys_cmd)
        os.system(sys_cmd)
        adc_file.close()

    def close(self,plot_id):
         plt.close(plot_id)
