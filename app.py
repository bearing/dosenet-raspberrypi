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
import pika
import argparse

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
#from PyQt5.QtGui import QStyleFactory
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
    if sensorName == "P/T/H":
        fileName = str("Pressure" + ".csv")
        pData = data[0]
        newRow = [lat, lon, pData]
        with open(fileName,'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(newRow)
            csvFile.close()
        fileName = str("Temperature" + ".csv")
        tData = data[1]
        newRow = [lat, lon, tData]
        with open(fileName,'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(newRow)
            csvFile.close()
        fileName = str("Humidity" + ".csv")
        hData = data[2]
        newRow = [lat, lon, hData]
        with open(fileName,'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(newRow)
            csvFile.close()
    else:
        fileName = str(sensorName + ".csv")
        newRow = [lat, lon, data]
        with open(fileName,'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(newRow)
            csvFile.close()


def createFile(sensorName):
    fileName = str(sensorName + ".csv")
    headerList = [['lat', 'lon', 'dataSet']]
    if os.path.exists(fileName) == False:
        with open(fileName, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(headerList)
            csvFile.close()

def createSaveFile():
    timeStamp = str(datetime.now())
    fileName = timeStamp + ".csv"
    print('fileName' + fileName)
    headerList = [['dateTime','latitude', 'longitude', 'airQuality', 'co2', 'humidity', 'pressure', 'radiation', 'temperature']]
    if os.path.exists(fileName) == False:
        with open(fileName, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(headerList)
            csvFile.close()
    return fileName

def appendSaveFile(sensors, lat, lon, saveName):
    now = datetime.now()
    dateTime = now.strftime("%d/%m/%Y %H:%M:%S")
    for x in range(len(sensors)):
        if x == 0:
            if 'Air Quality' in sensors:
                with open("AirQuality.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("AirQuality.csv")
                    col = f1['dataSet'].tolist()
                    air = col[-1]
            else:
                air = " "
        elif x == 1:
            if 'CO2' in sensors:
                with open("CO2.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("CO2.csv")
                    col = f1['dataSet'].tolist()
                    co2 = col[-1]
            else:
                co2 = " "
        elif x == 2:
            if 'H'in sensors:
                with open("Humidity.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("Humidity.csv")
                    col = f1['dataSet'].tolist()
                    hum = col[-1]
            else:
                hum = " "
        elif x == 3:
            if 'P' in sensors:
                with open("Pressure.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("Pressure.csv")
                    col = f1['dataSet'].tolist()
                    pres = col[-1]
            else:
                pres = " "
        elif x == 4:
            if 'RAD' in sensors:
                with open("Radiation.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("Radiation.csv")
                    col = f1['dataSet'].tolist()
                    RAD = col[-1]
            else:
                RAD = " "
        elif x == 5:
            if 'T' in sensors:
                with open("Temperature.csv", "r") as csvFile:
                    f1 = csv.reader(csvFile)
                    #f1 = pd.read_csv("Temperature.csv")
                    col = f1['dataSet'].tolist()
                    temp = col[-1]
            else:
                temp = " "

    newRow = [dateTime, lat, lon, air, co2, hum, pres, RAD, temp]
    with open(saveName,'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(newRow)
        csvFile.close()


def deleteFile():
    if os.path.exists("AirQuality.csv"):
      os.remove("AirQuality.csv")
    if os.path.exists("CO2.csv"):
      os.remove("CO2.csv")
    if os.path.exists("Humidity.csv"):
      os.remove("Humidity.csv")
    if os.path.exists("Pressure.csv"):
      os.remove("Pressure.csv")
    if os.path.exists("RAD.csv"):
      os.remove("RAD.csv")
    if os.path.exists("Temperature.csv"):
      os.remove("Temperature.csv")
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
                    {'label': 'Air Quality PM 2.5 (ug/m3)', 'value': 'airQuality'},
                    {'label': 'CO2', 'value': 'co2'},
                    {'label': 'Humidity', 'value': 'humidity'},
                    {'label': 'Pressure (Pa)', 'value': 'pressure'},
                    {'label': 'Radiation (cps)', 'value': 'RAD'},
                    {'label': 'Temperature (C)', 'value': 'temperature'}
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
            dcc.Checklist( id="airQuality",
                options=[{'label': 'Air Quality PM 2.5 (ug/m3)', 'value': 'airQuality'}], value=[]),
            dcc.Checklist( id="co2",
                options=[{'label': 'CO2', 'value': 'co2'}], value=[]),
            dcc.Checklist( id="humidity",
                options=[{'label': 'Humidity', 'value': 'humidity'}], value=[]),
            dcc.Checklist( id="pressure",
                options=[{'label': 'Pressure (Pa)', 'value': 'pressure'}], value=[]),
            dcc.Checklist( id="RAD",
                options=[{'label': 'Radiation (cps)', 'value': 'RAD'}], value=[]),
            dcc.Checklist( id="temperature",
                options=[{'label': 'Temperature (C)', 'value': 'temperature'}], value=[])])
        ], style= {'display': 'flex'}),

    html.Br(),
    html.Div(id='clicked-button', children='start:0 stop:0 last:0', style={'display': 'none'}),
    html.Div(id='display-clicked', children='', style={'display': 'none'}),
    html.Div(id='checked-sensor', children='', style={'display': 'none'}),
    html.Div(id='savingFileName', children='', style={'display': 'none'}),
    html.Div(id='collectingData', children='', style={'display': 'none'}),
    html.Div(id='savingData', children='', style={'display': 'none'}),

    html.Div(id='buttons', children = [
    html.Button(children = 'Start', id='start-button', n_clicks = 0, style={'width': "15%", 'height': "40px",'display': 'inline-block','margin-left': "10px",'margin-right': "30px", 'font_size': '40px'}),
    html.Button(children = 'Stop', id='stop-button', n_clicks = 0, style={'width': "15%", 'height': "40px", 'display': 'inline-block', 'margin-right': "30px", 'font_size': '40px'}),
    html.Button(children = 'Save', id='save-button', n_clicks = 0, style={'width': "15%", 'height': "40px", 'display': 'inline-block', 'font_size': '40px'})],
    style= {'margin-left': '20%','display': 'flex'}),

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
    [dash.dependencies.Input('start-button', 'n_clicks'),
    dash.dependencies.Input('stop-button', 'n_clicks')],
    [dash.dependencies.State('clicked-button', 'children'),
    dash.dependencies.State('intervalLoop', 'n_intervals')]
)
def updated_clicked(start_clicks, stop_clicks, prev_clicks, interval):
    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    if start_clicks > int(prev_clicks['start']):
        last_clicked = 'START'
    elif stop_clicks > int(prev_clicks['stop']):
        last_clicked = 'STOP'
        deleteFile()
        interval = 0
    else:
        last_clicked = "none"
    cur_clicks = 'start:{} stop:{} last:{}'.format(start_clicks, stop_clicks,last_clicked)

    return cur_clicks, interval

#return which sensors are clicked in array and makes files when start is clicked
@app.callback(
    dash.dependencies.Output('checked-sensor', 'children'),
    dash.dependencies.Input('start-button', 'n_clicks'),
    dash.dependencies.State('airQuality','value'),
    dash.dependencies.State('co2','value'),
    dash.dependencies.State('humidity','value'),
    dash.dependencies.State('pressure','value'),
    dash.dependencies.State('RAD','value'),
    dash.dependencies.State('temperature','value'))

def temp_sensor(start, air, co, hum, pres, rad, temp):
    sensorList = []
    if air != []:
        print ("air")
        createFile("AirQuality")
        sensorList.append("Air Quality")
    if co != []:
        print ("co2")
        createFile("CO2")
        sensorList.append("CO2")
    if hum != []:
        print ("hum")
        createFile("H")
        sensorList.append("Humidity")
    if pres != []:
        print ("pres")
        createFile("Pressure")
        createFile("Temperature")
        createFile("Humidity")
        sensorList.append("P/T/H")
    # if rad != []:
    #     print ("rad")
    #     createFile("RAD")
    #     sensorList.append("Radiation")
    # if temp != []:
    #     print ("temp")
    #     createFile("Temperature")
    #     sensorList.append("T")

    send_queue_cmd("START", sensorList) #start the sensors
    print(sensorList)
    return sensorList

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
    dash.dependencies.State('savingFileName', 'children'))
def collectDataInFile(n, clicked, save, sensors, fileName):
    last_clicked = clicked[-5:]
    if last_clicked == 'START':
        lat = str(randolat())
        lon = str(randolon())
        for x in sensors:
            messages = receive_queue_data()
            keys = messages.values()
            value = itr(keys)
            data = next(value)
            appendFile(x, lat, lon, value)
        if (save != 0):
            appendSaveFile(sensors, lat, lon, fileName)

        clear_queue()
    return "data"


# #read the file of correct sensor and display on map
@app.callback(
    dash.dependencies.Output('map', 'figure'),
    dash.dependencies.Input('intervalLoop', 'n_intervals'),
    dash.dependencies.State('clicked-button', 'children'),
    dash.dependencies.State('displayOption', 'value'))
def updateGraph(n, button, sensor):
    clicked = button[-1:]
    fileName = str(sensor + ".csv")
    if clicked == "t" and os.path.exists(fileName):
        fileName = sensor + ".csv"
        with open(fileName, "r") as csvFile:
            dataFile = csv.reader(csvFile)
        #dataFile = pd.read_csv(fileName)
        if len(dataFile["lat"]) != 0:
            # print ("in update graph creating trace")
            # print(dataFile['lat'])
            scl = [0,"rgb(150,0,90)"],[0.125,"rgb(0, 0, 200)"],[0.25,"rgb(0, 25, 255)"],\
            [0.375,"rgb(0, 152, 255)"],[0.5,"rgb(44, 255, 150)"],[0.625,"rgb(151, 255, 0)"],\
            [0.75,"rgb(255, 234, 0)"],[0.875,"rgb(255, 111, 0)"],[1,"rgb(255, 0, 0)"]

            fig = px.scatter_mapbox(
                dataFile,
                lat=dataFile['lat'],
                lon=dataFile['lon'],
                hover_name= dataFile['dataSet'],
                hover_data= {'dataSet':False},
                color=dataFile['dataSet'],
                color_continuous_scale=scl,
                zoom=19,
                height=1000,
                mapbox_style="open-street-map"
                )

            fig.update_geos(fitbounds="locations")
            fig.update_traces(marker={'size': 10})
            return fig
        return dash.no_update
    return dash.no_update
# ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=True)


#-------------------------------------------------------------------------------
# Methods for communication with the shared queue
#   - allows commmunication between GUI and sensor DAQs
#   - send commands and receive sensor data
#-------------------------------------------------------------------------------
def send_queue_cmd(cmd, daq_list):
    print("in send_queue_cmd")
    '''
    Send commands for sensor DAQs
        - valid commands: START, STOP, EXIT
    '''
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
    print("in receive_queue_data")
    '''
    Receive data from sensor DAQs
    '''
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='toGUI')
    method_frame, header_frame, body = channel.basic_get(queue='toGUI')
    if body is not None:
        HEAD
        # message from d3s seems to come back as bytes...
        # message from d3s is coming back as bytes
        d4b986b040e7ae16a0f57b5a4363212f294f6628
        if type(body) is bytes:
            body = body.decode("utf-8")
        message = json.loads(body)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        print("receivemess", message)
        return message
    else:
        print("NONE")
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
    # # Wrap everything in try/except so that sensor DAQs can be shutdown cleanly
    # try:
    #     if not arg_dict['test']:
    #         clear_queue()
    #     app = QApplication(sys.argv)
    #     #QApplication.setStyle(QStyleFactory.create("Cleanlooks"))
    #     nbins = 1024
    #     #ex = App(nbins=nbins, **arg_dict)
    #     #ex.show()
    #
    #     atexit.register(ex.exit)
    # except:
    #     if not arg_dict['test']:
    #         send_queue_cmd('EXIT',["Radiation","Air Quality","CO2","P/T/H"])
    #     # Still want to see traceback for debugging
    #     print('ERROR: GUI quit unexpectedly!')
    #     traceback.print_exc()
    #     pass
    #
    # ret = app.exec_()
    # print(ret)
    # sys.exit(ret)
