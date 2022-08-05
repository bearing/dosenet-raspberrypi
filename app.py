import os
from random import randint
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os.path
import decimal
import random
import csv
from os import path
from datetime import datetime
import datetime as dt
import pika
import argparse
import time

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import json
import sys
import traceback

app = dash.Dash(__name__, prevent_initial_callbacks=True)
# ________________________________________________________
# method that creates rando numbers
def randoNum():
    return randint(0, 46) * 8 + 13
def randolat():
    lat = 37.871591 + random.uniform(-0.0005, 0.0005)
    return lat
def randolon():
    lon = -122.261996 + random.uniform(-0.0005, 0.0005)
    return lon

def appendFile(sensorName, lat, lon, data):
    fileName = str(sensorName + ".csv")
    newRow = [lat, lon, data]
    with open(fileName,'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(newRow)
        csvFile.close()

def createFile(sensorName):
    print("created file with name: " + sensorName)
    fileName = str(sensorName + ".csv")
    headerList = [['lat', 'lon', 'dataSet']]
    if os.path.exists(fileName) == False:
        with open(fileName, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(headerList)
            csvFile.close()

def createSaveFile():
    timeStamp = str(datetime.now())
    fileName = str(timeStamp + ".csv")
    print('fileName' + fileName)
    headerList = [['dateTime','lat', 'lon', 'AirQuality', 'CO2', "Radiation", "Pressure", "Temperature", "Humidity"]]
    if os.path.exists(fileName) == False:
        with open(fileName, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(headerList)
            csvFile.close()
    return fileName

def appendSaveFile(sensorList, lat, lon, saveName, PTHSensor):
    now = datetime.now()
    dateTime = now.strftime("%d/%m/%Y %H:%M:%S")
    for x in range(len(sensors)):
        if x == 0:
            if 'AirQuality' in sensorList:
                with open("AirQuality.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("AirQuality.csv")
                    col = f1['dataSet'].tolist()
                    air = col[-1]
            else:
                air = " "
        elif x == 1:
            if 'CO2' in sensorList:
                with open("CO2.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("CO2.csv")
                    col = f1['dataSet'].tolist()
                    co2 = col[-1]
            else:
                co2 = " "
        elif x == 2:
            if 'Radiation' in sensorList:
                with open("Radiation.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("Radiation.csv")
                    col = f1['dataSet'].tolist()
                    rad = col[-1]
            else:
                RAD = " "
        elif x == 3:
            if 'P/T/H' in sensorList:
                if 'pres' in PTHSensor: #pressure
                    with open("P/T/H.csv", "r") as csvFile:
                        f1 = csv.reader(csvFile)
                        #f1 = pd.read_csv("Humidity.csv")
                        col = f1['dataSet'][0].tolist()
                        pres = col[-1]
                else:
                    pres = " "
                if 'temp' in PTHSensor:
                    with open("P/T/H.csv", "r") as csvFile:
                        f1 = csv.reader(csvFile)
                        #f1 = pd.read_csv("Temperature.csv")
                        col = f1['dataSet'][1].tolist()
                        temp = col[-1]
                else:
                    temp = " "
                if 'hum' in PTHSensor: #pressure
                    with open("P/T/H.csv", "r") as csvFile:
                        f1 = csv.reader(csvFile)
                        #f1 = pd.read_csv("Humidity.csv")
                        col = f1['dataSet'][2].tolist()
                        hum = col[-1]
                else:
                    hum = " "

        # elif x == 3:
        #     if 'H'in sensors:
        #         with open("Humidity.csv", "r") as csvFile:
        #             f1 = csv.reader(csvFile)
        #             #f1 = pd.read_csv("Humidity.csv")
        #             col = f1['dataSet'].tolist()
        #             hum = col[-1]
        #     else:
        #         hum = " "
        # elif x == 4:
        #     if 'P' in sensors:
        #         with open("Pressure.csv", "r") as csvFile:
        #             f1 = csv.reader(csvFile)
        #             #f1 = pd.read_csv("Pressure.csv")
        #             col = f1['dataSet'].tolist()
        #             pres = col[-1]
        #     else:
        #         pres = " "
        # elif x == 5:
        #     if 'T' in sensors:
        #         with open("Temperature.csv", "r") as csvFile:
        #             f1 = csv.reader(csvFile)
        #             #f1 = pd.read_csv("Temperature.csv")
        #             col = f1['dataSet'].tolist()
        #             temp = col[-1]
        #     else:
        #         temp = " "

    newRow = [dateTime, lat, lon, air, co2, rad, pres, temp, hum]
    with open(saveName,'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(newRow)
        csvFile.close()


def deleteFile():
    if os.path.exists("AirQuality.csv"):
      os.remove("AirQuality.csv")
    if os.path.exists("CO2.csv"):
      os.remove("CO2.csv")
    if os.path.exists("P/T/H.csv"):
        os.remove("P/T/H.csv")
    if os.path.exists("Radiation.csv"):
      os.remove("Radiation.csv")
    else:
      print("The file does not exist")
#
# fig = go.Figure(go.Scattermapbox(mode = "markers", marker = {'size': 10}))
# fig.update_geos(fitbounds="locations")
# fig.update_layout(
#     mapbox = {
#         'style': "open-street-map"})
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("DoseNet Mapping Radiation", style={'text-align': 'center'}),
    html.Br(),
    html.Div(id = 'dropdownOne', children = [
        html.Div(id='timeText', children='How often should the sensors collect data?', style= {'margin-right': '2%'}),
        dcc.Dropdown(id="timeInterval",
            options=[
                {"label": "5 Seconds", "value": 5000},
                {"label": "2 Seconds", "value": 2000},
                {"label": "1 Second", "value": 1000},
                {"label": "0.5 Seconds", "value": 500}
            ],
            placeholder="Select a time",
            multi=False,
            value=1,
            style={'width': "40%", 'height': '30px'})],
        style= {'margin-bottom': '2%', 'margin-left': '5%', 'text-align': 'center', 'display': 'flex'}),

        html.Br(),
        html.Div(id = 'dropdownTwo', children = [
            html.Div(id='sensorText', children='What sensor data do you want to display on the map?', style= {'margin-right': '2%'}),
            dcc.Dropdown(id="displayOption",
                options=[
                    {'label': 'Air Quality PM 2.5 (ug/m3)', 'value': "AirQuality"},
                    {'label': 'CO2', 'value': 'CO2'},
                    {'label': 'Humidity', 'value': 'Humidity'},
                    {'label': 'Pressure (Pa)', 'value': 'Pressure'},
                    {'label': 'Radiation (cps)', 'value': 'Radiation'},
                    {'label': 'Temperature (C)', 'value': 'Temperature'}
                ],
                placeholder="Select a sensor",
                multi=False,
                value='',
                style={'width': "40%", 'height':'30px'})],
            style= {'margin-bottom': '2%','margin-left': '5%', 'text-align': 'center', 'display': 'flex'}),

    html.Br(),
    html.Div(id='checklist', children = [
        html.Div(id='checklistText', children='What sensors do you want to be collecting data?', style= {'margin-left': '5%', 'margin-right': '5%'}),
        html.Div(id='checkboxes', children = [
            dcc.Checklist( id="AirQuality",
                options=[{'label': 'Air Quality PM 2.5 (ug/m3)', 'value': 'AirQuality'}], value=[]),
            dcc.Checklist( id="CO2",
                options=[{'label': 'CO2', 'value': 'CO2'}], value=[]),
            dcc.Checklist( id="Humidity",
                options=[{'label': 'Humidity', 'value': 'Humidity'}], value=[]),
            dcc.Checklist( id="Pressure",
                options=[{'label': 'Pressure (Pa)', 'value': 'Pressure'}], value=[]),
            dcc.Checklist( id="Radiation",
                options=[{'label': 'Radiation (cps)', 'value': 'Radiation'}], value=[]),
            dcc.Checklist( id="Temperature",
                options=[{'label': 'Temperature (C)', 'value': 'Temperature'}], value=[])])
        ], style= {'display': 'flex'}),

    html.Br(),
    html.Div(id='clicked-button', children='', style={'display': 'none'}),
    html.Div(id='prevStart', children='0', style={'display': 'none'}),
    html.Div(id='prevStop', children='0', style={'display': 'none'}),
    html.Div(id='display-clicked', children='', style={'display': 'none'}),
    html.Div(id='checked-sensor', children='', style={'display': 'none'}),
    html.Div(id='savingFileName', children='', style={'display': 'none'}),
    html.Div(id='collectingData', children='', style={'display': 'none'}),
    html.Div(id='savingData', children='', style={'display': 'none'}),
    html.Div(id='PTHSensors', children='', style={'display': 'none'}),

    html.Div(id='buttons', children = [
    html.Button(children = 'Start', id='start-button', n_clicks = 0, style={'width': "15%", 'height': "40px",'display': 'inline-block','margin-right': "10%", 'font_size': '40px'}),
    html.Button(children = 'Stop', id='stop-button', n_clicks = 0, style={'width': "15%", 'height': "40px", 'display': 'inline-block', 'margin-right': "10%", 'font_size': '40px'}),
    html.Button(children = 'Save Data', id='save-button', n_clicks = 0, style={'width': "15%", 'height': "40px", 'display': 'inline-block', 'font_size': '40px', 'margin-right': "10%"}),
    html.Button('Download as HTML', id = 'download',  n_clicks = 0, style={'width': "15%", 'height': "40px", 'display': 'inline-block', 'font_size': '40px'})],
    style= {'text-align': 'center','margin-left': "8%",'margin-top': '5%', 'display': 'flex'}),

    html.Br(),

    dcc.Graph(id='map'),
    dcc.Interval(
            id = 'intervalLoop',
            interval = 1 * 5000,
            n_intervals = 0
        ),
    dcc.Interval(
            id = 'dataLoop',
            interval = 1 * 5000,
            n_intervals = 0
        ),
    dcc.Interval(
            id = 'saveLoop',
            interval = 1 * 5000,
            n_intervals = 0
        )
])
# ------------------------------------------------------------------------------
#tells us what button was the last one clicked
@app.callback(
    dash.dependencies.Output('clicked-button', 'children'),
    dash.dependencies.Output('intervalLoop', 'n_intervals'),
    dash.dependencies.Output('prevStart', 'children'),
    dash.dependencies.Output('prevStop', 'children'),
    [dash.dependencies.Input('start-button', 'n_clicks'),
    dash.dependencies.Input('stop-button', 'n_clicks')],
    [dash.dependencies.State('prevStart', 'children'),
    dash.dependencies.State('prevStop', 'children'),
    dash.dependencies.State('intervalLoop', 'n_intervals'),
    dash.dependencies.State('checked-sensor', 'children')])
def updatedClicked(start_clicks, stop_clicks, prevStart, prevStop, interval, sensorList):
    if start_clicks > int(prevStart):
        last_clicked = 'START'
        if start_clicks == 1:
            print("updatedClicked: start button pushed")
            clear_queue()
        prevStart = start_clicks
    elif stop_clicks > int(prevStop):
        last_clicked = 'STOP'
        interval = 0
        deleteFile()
        print("Sending EXIT command to all active sensors")
        send_queue_cmd('STOP',sensorList)
        send_queue_cmd('EXIT',sensorList)
        time.sleep(2)
        prevStop = stop_clicks
        return("exit")
    else:
        last_clicked = 'none'
    print('updatedClicked: ', last_clicked )
    return last_clicked, interval, prevStart, prevStop

#return which sensors are clicked in array and makes files when start is clicked
@app.callback(
    dash.dependencies.Output('checked-sensor', 'children'),
    dash.dependencies.Output('PTHSensors', 'children'), ###MAKE SURE THIS WORKS AND DONT FORGET####
    dash.dependencies.Input('start-button', 'n_clicks'),
    dash.dependencies.State('AirQuality','value'),
    dash.dependencies.State('CO2','value'),
    dash.dependencies.State('Humidity','value'),
    dash.dependencies.State('Pressure','value'),
    dash.dependencies.State('Radiation','value'),
    dash.dependencies.State('Temperature','value'))
def startProcess(start, air, co, hum, pres, rad, temp):
    sensorList = []
    PTHSens = []
    if air != []:
        print ("startProcess: selected air")
        createFile('AirQuality')
        sensorList.append('AirQuality')
    if co != []:
        print ("startProcess: selected co2")
        createFile('CO2')
        sensorList.append('CO2')
    if rad != []:
        print ("startProcess: selected rad")
        createFile('Radiation')
        sensorList.append('Radiation')
    if pres != [] or hum != [] or temp != []:
        print ("startProcess: selected PTH")
        createFile("P/T/H")
        sensorList.append('P/T/H')
        if pres != []:
            PTHSens.append("pres")
        if temp != []:
            PTHSens.append("temp")
        if hum != []:
            PTHSens.append("hum")
    print("startProcess: sensorList: " , sensorList)
    startSensor(sensorList)
    print("startProcess: startSensors called")
    time.sleep(2)
    send_queue_cmd("START", sensorList)
    print("startProcess: send_queue_cmd called")
    return sensorList, PTHSens

#creates file to save the data onto
@app.callback(
    dash.dependencies.Output('savingFileName', 'children'),
    dash.dependencies.Input('save-button', 'n_clicks'))
def saveFile(save):
    return createSaveFile()

#collect data and append to files continuously for time interval after start pushed. saves the data onto the file if the save button has been pushed
@app.callback(
    dash.dependencies.Output('collectingData', 'children'),
    dash.dependencies.Input('dataLoop', 'n_intervals'),
    dash.dependencies.State('clicked-button', 'children'),
    dash.dependencies.State('save-button', 'n_clicks'),
    dash.dependencies.State('checked-sensor', 'children'),
    dash.dependencies.State('savingFileName', 'children'),
    dash.dependencies.State('PTHSensors', 'children'))
def collectDataInFile(n, clicked, save, sensorList, fileName, PTHSensor):
    last_clicked = clicked[-1:]
    if last_clicked == 'T':
        lat = str(randolat())
        lon = str(randolon())
        for sensor in sensorList:
            messages = receive_queue_data()
            if messages is not None:
                data = sum(messages['data'])
                print("collectDataInFile: sum of the data: " , data)
                appendFile(sensor, lat, lon, data)
        if (save != 0):
            appendSaveFile(sensorList, lat, lon, fileName, PTHSensor)
            print("collectDataInFile: appendSaveFile")
        return "data"

# #read the file of correct sensor and display on map
@app.callback(
    dash.dependencies.Output('map', 'figure'),
    dash.dependencies.Output('download', 'n_clicks'),
    dash.dependencies.Input('intervalLoop', 'n_intervals'),
    dash.dependencies.State('clicked-button', 'children'),
    dash.dependencies.State('displayOption', 'value'),
    dash.dependencies.State('download', 'n_clicks'))
def updateGraph(n, button, sensor, save):
    clicked = button[-1:]
    print("started it")
    href = None
    if clicked == "T":
        fileName = str(sensor + ".csv")
        if os.path.exists(fileName):
            print("past here")
            fileName = sensor + ".csv"
            dataFile = pd.read_csv(fileName)
            if len(dataFile["lat"]) != 0:
                print("in update graph creating trace")
                scl = [0,"rgb(150,0,90)"],[0.125,"rgb(0, 0, 200)"],[0.25,"rgb(0, 25, 255)"],\
                [0.375,"rgb(0, 152, 255)"],[0.5,"rgb(44, 255, 150)"],[0.625,"rgb(151, 255, 0)"],\
                [0.75,"rgb(255, 234, 0)"],[0.875,"rgb(255, 111, 0)"],[1,"rgb(255, 0, 0)"]
                fig = px.scatter_mapbox(
                    lat=dataFile['lat'],
                    lon=dataFile['lon'],
                    hover_name= dataFile['dataSet'],
                    #hover_data= {dataFile['dataSet']:False},
                    color=dataFile['dataSet'],
                    color_continuous_scale=scl,
                    zoom=19,
                    height=1000,
                    mapbox_style="open-street-map"
                    )
                fig.update_geos(fitbounds="locations")
                fig.update_traces(marker={'size': 10})
                if save != 0:
                    print("in the save part")
                    timeStamp = datetime.now()
                    title = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
                    fig.write_html(str(title) + ".html")
                    save = 0
                return fig, save
            return dash.no_update
    return dash.no_update
# ------------------------------------------------------------------------------
# if __name__ == '__main__':
     #app.run_server(debug=True)
#________________________________________________________________________________
def startSensor(sensorList):
    file_prefix = '{}_p{}_g{}'.format("Inside", "1", "1")
    fname = "/home/pi/data/" + file_prefix + '_' + \
    str(dt.datetime.today()).split()[0]
    py = 'sudo python'
    for sensor in sensorList:
        if sensor == 'P/T/H':
            py = 'python3'
            script = 'weather_DAQ_rabbitmq.py'
            log = 'weather_gui.log'

        if sensor == 'AirQuality':
            py = 'python'
            script = 'air_quality_DAQ.py'
            log = 'AQ_gui.log'

        if sensor == 'Radiation':
            print("here: RAD")
            py = 'sudo python2'
            script = 'D3S_rabbitmq_DAQ.py'
            log = 'rad_gui.log'

        if sensor == 'CO2':
            py = 'python'
            script = 'adc_DAQ.py'
            log = 'CO2_gui.log'

        cmd_head = '{} /home/pi/pyqt-gui/dosenet-raspberrypi/{}'.format(py, script)
        cmd_options = ' -i {}'.format("2")
        cmd_log = ' > /tmp/{} 2>&1 &'.format(log)
        cmd = cmd_head + cmd_options + cmd_log
        print("startSensor: completed")
        os.system(cmd)

#-------------------------------------------------------------------------------
# Methods for communication with the shared queue
#   - allows commmunication between GUI and sensor DAQs
#   - send commands and receive sensor data
#-------------------------------------------------------------------------------
def send_queue_cmd(cmd, daq_list):
    '''
    Send commands for sensor DAQs
        - valid commands: START, STOP, EXIT
    '''
    print("in send q")
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='fromGUI')
    for sensor in daq_list:
        print("Sending cmd: {} for {}".format(cmd,sensor))
        message = {'id': sensor, 'cmd': cmd}
        channel.basic_publish(exchange='',
                              routing_key='fromGUI',
                              body=json.dumps(message))
    connection.close()

def receive_queue_data():
    '''
    Receive data from sensor DAQs
    '''
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='toGUI')
    method_frame, header_frame, body = channel.basic_get(queue='toGUI')
    if body is not None:
        # message from d3s is coming back as bytes
        if type(body) is bytes:
            body = body.decode("utf-8")
        message = json.loads(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        return message
    else:
        connection.close()
        return None

def clear_queue():
    print("Initializing queues... clearing out old data")
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='toGUI')
    channel.queue_delete(queue='toGUI')
    connection.close()

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='fromGUI')
    channel.queue_delete(queue='fromGUI')
    connection.close()


if __name__ == '__main__':
    app.run_server(debug=True)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", "-t",
        action='store_true',
        default=False,
    )
    parser.add_argument(
        "--windows", "-w",
        action = 'store_true',
        default = False,
    )

    args = parser.parse_args()
    arg_dict = vars(args)

    # global ex
    # #Wrap everything in try/except so that sensor DAQs can be shutdown cleanly
    # try:
    #     if not arg_dict['test']:
    #         clear_queue()
    #     app = QApplication(sys.argv)
    #     QApplication.setStyle(QStyleFactory.create("Cleanlooks"))
    #     nbins = 1024
    #     # ex = App(nbins=nbins, **arg_dict)
    #     # ex.show()
    #
    #     #atexit.register(ex.exit)
    # except:
    #     if not arg_dict['test']:
    #         send_queue_cmd('EXIT',[RAD,AIR,CO2,PTH])
    #     # Still want to see traceback for debugging
    #     print('ERROR: GUI quit unexpectedly!')
    #     traceback.print_exc()
    #     pass

    # ret = app.exec_()
    # print(ret)
    # sys.exit(ret)
