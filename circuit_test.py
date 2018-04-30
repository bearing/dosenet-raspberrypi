import time
import sys
from managers import Manager_Pocket
from managers import Manager_AQ
from managers import Manager_CO2
from managers import Manager_Weather
from globalvalues import ANSI_RESET, ANSI_GR, ANSI_RED, ANSI_CYAN, ANSI_YEL
from globalvalues import CIRCUIT_SENSOR_NAMES
from globalvalues import SINGLE_BREAK_LINE, DOUBLE_BREAK_LINE
from globalvalues import INTERVAL_QUESTION, SENSOR_CONNECTION_QUESTION
from globalvalues import CIRCUIT_TEST_RUNNING, CIRCUIT_TEST_RETRYING
from globalvalues import CPM_DISPLAY_TEXT
from globalvalues import AQ_PM_DISPLAY_TEXT, AQ_P_DISPLAY_TEXT
from globalvalues import CO2_DISPLAY_TEXT
from globalvalues import WEATHER_DISPLAY_TEXT
from globalvalues import AQ_VARIABLES, WEATHER_VARIABLES, CO2_VARIABLES

"""
Code meant to make it easy to test newly soldered PiHats without knowing
how to run the other managment code.

This code also takes into account all possibilities of users inputting
answers to questions that will not lead to anything: ie 'x' instead of 'yes'

It prints out found data which allows the user to determine whether or not
the circuit is functioning properly. It also gives users the option to retry without rerunning
this testing code, along with giving a couple helpful hints to help determine
possible things that could cause problems with sensors working properly.
"""

sensors, question = [], SENSOR_CONNECTION_QUESTION
names, running, retrying = CIRCUIT_SENSOR_NAMES, CIRCUIT_TEST_RUNNING, CIRCUIT_TEST_RETRYING
for sensor in range(4):
    ansr_err = True
    while ansr_err:
        sensor_i = input(question.format(sensor_name=names[sensor])).upper()
        if sensor_i not in ['YES', 'Y', 'NO', 'N']:
            print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET))
        else:
            ansr_err = False
    sensors.append(sensor_i)
print(SINGLE_BREAK_LINE)
int_err = True
while int_err:
    try:
        interval = int(input(INTERVAL_QUESTION))
        int_err = False
    except ValueError:
        print('{red}Please enter a time in seconds as a number. {reset}'.format(red=ANSI_RED, reset=ANSI_RESET))
print(DOUBLE_BREAK_LINE)

if sensors[0] == 'YES' or sensors[0] == 'Y':
    sensor_pocket = Manager_Pocket(cirtest=True, new_setup=new_setup)
    pocket = True
if sensors[1] == 'YES' or sensors[1] == 'Y':
    sensor_AQ = Manager_AQ(cirtest=True, new_setup=new_setup)
    AQ = True
if sensors[2] == 'YES' or sensors[2] == 'Y':
    sensor_CO2 = Manager_CO2(cirtest=True, new_setup=new_setup)
    CO2 = True
if sensors[3] == 'YES' or sensors[3] == 'Y':
    sensor_weather = Manager_Weather(cirtest=True, new_setup=new_setup)
    Weather = True

if pocket:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing = True, True
    while testing:
        if first_run:
            print(running.format(sensor_name=names[0], interval=interval))
            first_run = False
        else:
            print(retrying.format(sensor_name=names[0], interval=interval))
        counts, cpm, cpm_err = sensor_pocket.handle_data(start_time, end_time, None)
        if counts != 0:
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[0]))
            print(CPM_DISPLAY_TEXT.format(counts=counts, cpm=cpm, cpm_err=cpm_err))
            print(DOUBLE_BREAK_LINE)
            testing = False
        else:
            print('{red}No data found from the {sensor}!{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET, sensor=names[0]))
            print('{red}Either the interval was too short, the sensor is not connected or {reset}' +
                '{red}no data was found.{reset}'.format(red=ANSI_RED, reset=ANSI_RESET))
            print('{red}Make sure the sensor is connected and try again to determine whether it is the circuit or not.{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET))
            ansr_err = True
            while ansr_err:
                retry = input('{yellow}Would you like to try again?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                if retry not in ['YES', 'Y', 'NO', 'N']:
                    print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                        red=ANSI_RED, reset=ANSI_RESET))
                else:
                    ansr_err = False
            if retry == 'NO' or retry == 'N':
                ansr_err = True
                while ansr_err:
                    cont = input('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if cont not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if cont == 'NO' or cont == 'N':
                    sys.exit()
                testing = False
            else:
                ansr_err = True
                while ansr_err:
                    change_int = input('{yellow}Would you like to change the time interval?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if change_int not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if change_int == 'YES' or change_int == 'Y':
                    int_err = True
                    while int_err:
                        try:
                            interval_new = int(input(INTERVAL_QUESTION))
                            int_err = False
                        except ValueError:
                            print('{red}Please enter a time in seconds as a number. {reset}'.format(
                                red=ANSI_RED, reset=ANSI_RESET))
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
if AQ:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing = True, True
    while testing:
        if first_run:
            print(running.format(sensor_name=names[1], interval=interval))
            first_run = False
        else:
            print(retrying.format(sensor_name=names[1], interval=interval))
        average_data = sensor_AQ.handle_data(start_time, end_time, None)
        if any(data != 0 for data in average_data):
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[1]))
            for i in range(3):
                print(AQ_PM_DISPLAY_TEXT.format(variable=AQ_VARIABLES[i], avg_data=average_data[i]))
            for i in range(3, 9):
                print(AQ_P_DISPLAY_TEXT.format(variable=AQ_VARIABLES[i], avg_data=average_data[i]))
            print(DOUBLE_BREAK_LINE)
            testing = False
        else:
            print('{red}No data found from the {sensor}!{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET, sensor=names[1]))
            print('{red}Either the interval was too short, the sensor is not connected or {reset}' +
                '{red}no data was found.{reset}'.format(red=ANSI_RED, reset=ANSI_RESET))
            print('{red}Make sure the sensor is connected and try again to determine whether it is the circuit or not.{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET))
            ansr_err = True
            while ansr_err:
                retry = input('{yellow}Would you like to try again?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                if retry not in ['YES', 'Y', 'NO', 'N']:
                    print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                        red=ANSI_RED, reset=ANSI_RESET))
                else:
                    ansr_err = False
            if retry == 'NO' or retry == 'N':
                ansr_err = True
                while ansr_err:
                    cont = input('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if cont not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if cont == 'NO' or cont == 'N':
                    sys.exit()
                testing = False
            else:
                ansr_err = True
                while ansr_err:
                    change_int = input('{yellow}Would you like to change the time interval?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if change_int not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if change_int == 'YES' or change_int == 'Y':
                    int_err = True
                    while int_err:
                        try:
                            interval_new = int(input(INTERVAL_QUESTION))
                            int_err = False
                        except ValueError:
                            print('{red}Please enter a time in seconds as a number. {reset}'.format(
                                red=ANSI_RED, reset=ANSI_RESET))
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
if CO2:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing = True, True
    while testing:
        if first_run:
            print(running.format(sensor_name=names[2], interval=interval))
            first_run = False
        else:
            print(retrying.format(sensor_name=names[2], interval=interval))
        average_data = sensor_CO2.handle_data(start_time, end_time, None)
        if any(data != 0 for data in average_data):
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[2]))
            for i in range(len(CO2_VARIABLES)):
                print(CO2_DISPLAY_TEXT.format(variable=CO2_VARIABLES[i], data=average_data[i]))
            print(DOUBLE_BREAK_LINE)
            testing = False
        else:
            print('{red}No data found from the {sensor}!{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET, sensor=names[2]))
            print('{red}Either the interval was too short, the sensor is not connected or {reset}' +
                '{red}no data was found.{reset}'.format(red=ANSI_RED, reset=ANSI_RESET))
            print('{red}Make sure the sensor is connected and try again to determine whether it is the circuit or not.{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET))
            ansr_err = True
            while ansr_err:
                retry = input('{yellow}Would you like to try again?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                if retry not in ['YES', 'Y', 'NO', 'N']:
                    print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                        red=ANSI_RED, reset=ANSI_RESET))
                else:
                    ansr_err = False
            if retry == 'NO' or retry == 'N':
                ansr_err = True
                while ansr_err:
                    cont = input('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if cont not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if cont == 'NO' or cont == 'N':
                    sys.exit()
                testing = False
            else:
                ansr_err = True
                while ansr_err:
                    change_int = input('{yellow}Would you like to change the time interval?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if change_int not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if change_int == 'YES' or change_int == 'Y':
                    int_err = True
                    while int_err:
                        try:
                            interval_new = int(input(INTERVAL_QUESTION))
                            int_err = False
                        except ValueError:
                            print('{red}Please enter a time in seconds as a number. {reset}'.format(
                                red=ANSI_RED, reset=ANSI_RESET))
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
if Weather:
    print(running.format(sensor_name=names[3], interval=interval))
    average_data = sensor_weather.handle_data(start_time, end_time, None)
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing = True, True
    while testing:
        if first_run:
            print(running.format(sensor_name=names[3], interval=interval))
            first_run = False
        else:
            print(retrying.format(sensor_name=names[3], interval=interval))
        average_data = sensor_weather.handle_data(start_time, end_time, None)
        if any(data != 0 for data in average_data):
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[3]))
            for i in range(len(CO2_VARIABLES)):
                print(WEATHER_DISPLAY_TEXT.format(variable=CO2_VARIABLES[i], data=average_data[i]))
            print(DOUBLE_BREAK_LINE)
            testing = False
        else:
            print('{red}No data found from the {sensor}!{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET, sensor=names[3]))
            print('{red}Either the interval was too short, the sensor is not connected or {reset}' +
                '{red}no data was found.{reset}'.format(red=ANSI_RED, reset=ANSI_RESET))
            print('{red}Make sure the sensor is connected and try again to determine whether it is the circuit or not.{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET))
            ansr_err = True
            while ansr_err:
                retry = input('{yellow}Would you like to try again?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                if retry not in ['YES', 'Y', 'NO', 'N']:
                    print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                        red=ANSI_RED, reset=ANSI_RESET))
                else:
                    ansr_err = False
            if retry == 'NO' or retry == 'N':
                ansr_err = True
                while ansr_err:
                    cont = input('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if cont not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if cont == 'NO' or cont == 'N':
                    sys.exit()
                testing = False
            else:
                ansr_err = True
                while ansr_err:
                    change_int = input('{yellow}Would you like to change the time interval?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET)).upper()
                    if change_int not in ['YES', 'Y', 'NO', 'N']:
                        print('{red}Please enter one of the following: Yes, Y, No, or N{reset}'.format(
                            red=ANSI_RED, reset=ANSI_RESET))
                    else:
                        ansr_err = False
                if change_int == 'YES' or change_int == 'Y':
                    int_err = True
                    while int_err:
                        try:
                            interval_new = int(input(INTERVAL_QUESTION))
                            int_err = False
                        except ValueError:
                            print('{red}Please enter a time in seconds as a number. {reset}'.format(
                                red=ANSI_RED, reset=ANSI_RESET))
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
