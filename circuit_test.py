import time
import sys
import argparse
from globalvalues import RPI
from managers import Manager_Pocket
from managers import Manager_AQ
from managers import Manager_CO2
from managers import Manager_Weather
from managers import SleepError
from globalvalues import ANSI_RESET, ANSI_GR, ANSI_RED, ANSI_CYAN, ANSI_YEL
from globalvalues import CIRCUIT_SENSOR_NAMES
from globalvalues import SINGLE_BREAK_LINE, DOUBLE_BREAK_LINE
from globalvalues import INTERVAL_QUESTION, SENSOR_CONNECTION_QUESTION, DATA_LOGGING_QUESTION
from globalvalues import CIRCUIT_TEST_RUNNING, CIRCUIT_TEST_RETRYING
from globalvalues import CPM_DISPLAY_TEXT
from globalvalues import AQ_PM_DISPLAY_TEXT, AQ_P_DISPLAY_TEXT
from globalvalues import CO2_DISPLAY_TEXT
from globalvalues import WEATHER_DISPLAY_TEXT
from globalvalues import AQ_VARIABLES, WEATHER_VARIABLES, CO2_VARIABLES, WEATHER_VARIABLES_UNITS

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

parser = argparse.ArgumentParser()
parser.add_argument(
    '--old_led_pins', '-o', action='store_true', default=False,
    help='Activate this flag this if the board has the much older LED pin layout.')
parser.add_argument(
    '--log', '-l', action='store_true', default=False,
    help='Activate this flag if you would like to store the data from testing the board.')

args = parser.parse_args()
arg_dict = vars(args)

print(arg_dict)

if not RPI:
    print(SINGLE_BREAK_LINE)
    print(('{red}This is not being executed on a RaspberryPi, none of the rest of {reset}' +
        '{red}this program \nwill function properly. Please try executing this again {reset}' +
        '{red}on an actual device.\n\nHowever, if this is being run on a RaspberryPi and you {reset}' +
        '{red}are seeing this \nerror, make sure the default package for the GPIO pins {reset}' +
        '{red}has not been \ndeleted for some strange reason.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))
    print(SINGLE_BREAK_LINE)
    sys.exit()

def ques_conv(question, int_vers=False, restr=True, ans_choices=('Y','YES','N','NO','EXIT')):
    """
    Can record answers in either string or integer format, also in string mode,
    evaluates whether a given user input is a valid response based on either the
    default answer choices or an optional inputted choice set.
    If the default answer set is used, it converts the user answer to True/False
    depending on whether they entered y/yes or n/no respectively.

    In integer mode, validates the user input type to make sure it is a number,
    then outputs the user answer.

    At any point during any question, the user may enter "exit" which terminates
    the program.
    """
    default_answer_choices = ('Y','YES','N','NO','EXIT')
    if ans_choices == default_answer_choices:
        choices = str(ans_choices[:4])[1:-1]
        def_choices = True
    else:
        ans_choices = [choice.upper() for choice in ans_choices]
        choices = str(ans_choices)[1:-1]
        def_choices = False
    ansr_err, int_err = True, True
    if not int_vers:
        while ansr_err:
            ans = raw_input(question).upper()
            if restr:
                if ans not in ans_choices:
                    print('{red}Please enter one of the following: {choices}{reset}'.format(
                        red=ANSI_RED, choices=choices, reset=ANSI_RESET))
                else:
                    ansr_err = False
            else:
                ansr_err = False
        if restr and def_choices:
            if ans == 'YES' or ans == 'Y':
                ans = True
            elif ans == 'EXIT':
                sys.exit()
            elif ans == 'NO' or ans == 'N':
                ans = False
    else:
        while int_err:
            ans = raw_input(question)
            try:
                if ans.upper() == 'EXIT':
                    sys.exit()
            except AttributeError:
                pass
            if ans.strip():
                try:
                    ans = int(round(float(ans)))
                    if restr and not def_choices:
                        if ans not in ans_choices:
                            print('{red}Please enter one of the following: {choices}{reset}'.format(
                                red=ANSI_RED, choices=choices, reset=ANSI_RESET))
                        else:
                            int_err = False
                    else:
                        int_err = False
                except ValueError:
                    print('{red}Please enter a time in seconds as a number. {reset}'.format(
                        red=ANSI_RED, reset=ANSI_RESET))
            else:
                ans = 30
                print('{green}No interval given, using default testing interval of 30 seconds.{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET))
                int_err = False
    return ans

sensors, ansr_err, int_err, new_setup = [], True, True, True
names, running, retrying = CIRCUIT_SENSOR_NAMES, CIRCUIT_TEST_RUNNING, CIRCUIT_TEST_RETRYING
pocket_data, AQ_data, CO2_data, weather_data = None, None, None, None
sensor_question, data_question = SENSOR_CONNECTION_QUESTION, DATA_LOGGING_QUESTION

print(SINGLE_BREAK_LINE)
if not ques_conv('{green}Does this PiHat have the new LED configuration?  {reset}'.format(
    green=ANSI_GR, reset=ANSI_RESET)):
    new_setup = False
print('\n')
for sensor in range(4):
    sensor_i, sensor_i2 = ques_conv(sensor_question.format(sensor_name=names[sensor])), None
    if sensor_i:
        sensor_i2 = ques_conv(data_question.format(sensor_name=names[sensor]))
    sensors.append((sensor_i, sensor_i2))
print('\n')
if not any(ans[0] for ans in sensors):
    print(('{red}Shutting down program since no sensors are connected.{reset}').format(
        red=ANSI_RED, reset=ANSI_RESET))
    print(SINGLE_BREAK_LINE)
    sys.exit()
interval = ques_conv(INTERVAL_QUESTION, True)
print(DOUBLE_BREAK_LINE)

pocket, AQ, CO2, Weather = False, False, False, False
if sensors[0][0]:
    if sensors[0][1]:
        sensor_pocket = Manager_Pocket(cirtest=True, interval=interval, new_setup=new_setup, datalogflag=True)
    else:
        sensor_pocket = Manager_Pocket(cirtest=True, interval=interval, new_setup=new_setup)
    pocket, pocket_data = True, False
if sensors[1][0]:
    if sensors[1][1]:
        sensor_AQ = Manager_AQ(cirtest=True, interval=interval, new_setup=new_setup, datalogflag=True)
    else:
        sensor_AQ = Manager_AQ(cirtest=True, interval=interval, new_setup=new_setup)
    AQ, AQ_data = True, False
if sensors[2][0]:
    if sensors[2][1]:
        sensor_CO2 = Manager_CO2(cirtest=True, interval=interval, new_setup=new_setup, datalogflag=True)
    else:
        sensor_CO2 = Manager_CO2(cirtest=True, interval=interval, new_setup=new_setup)
    CO2, CO2_data = True, False
if sensors[3][0]:
    try:
        if sensors[3][1]:
            sensor_weather = Manager_Weather(cirtest=True, interval=interval, new_setup=new_setup, datalogflag=True)
        else:
            sensor_weather = Manager_Weather(cirtest=True, interval=interval, new_setup=new_setup)
        Weather, weather_data = True, False
    except NameError:
        print(('{red}Could not import the Weather Port and thus could not initiate \n{reset}' +
            '{red}the Weather Sensor. This usually means that the Weather Sensor \n{reset}' +
            '{red}is not actually connected to the RaspberryPi. It could also mean that \n{reset}' +
            '{red}the Weather Sensor itself is not working, check to see that \n{reset}' +
            '{red}the sensor is actually connected, if it is then try restarting the RaspberryPi. \n{reset}' +
            '{red}If none of this works then check both the Weather Sensor and the PiHat \n{reset}' +
            '{red}for any places that the circuitry could fail.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))

if pocket:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing, interval_new, counts = True, True, None, 0
    while testing:
        slpskp = False
        if first_run:
            print(running.format(sensor_name=names[0], interval=interval))
            first_run = False
        else:
            print('\n')
            if interval_new != None:
                print(retrying.format(sensor_name=names[0], interval=interval_new))
            else:
                print(retrying.format(sensor_name=names[0], interval=interval))
        try:
            sensor_pocket.sleep_until(end_time)
        except SleepError:
            print(('{red}SleepError: system clock skipped ahead! This happens every once in a while {reset}' +
                '{red}just try again and it should work. {reset}').format(
                red=ANSI_RED, reset=ANSI_RESET))
            slpskp = True
        if not slpskp:
            counts, cpm, cpm_err = sensor_pocket.handle_data(start_time, end_time, None)
        if counts != 0 and not slpskp:
            pocket_data = True
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[0]))
            print(CPM_DISPLAY_TEXT.format(counts=counts, cpm=cpm, cpm_err=cpm_err))
            testing = False
        else:
            if not slpskp:
                print('{red}No data found from the {sensor}!{reset}'.format(
                    red=ANSI_RED, reset=ANSI_RESET, sensor=names[0]))
                print(('{red}Either the interval was too short, the sensor is not connected or no data\n{reset}' +
                    '{red}was found. Make sure the sensor is connected and try again to determine\n{reset}' +
                    '{red}whether it is the circuit or not.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))
            print('\n')
            retry = ques_conv('{yellow}Would you like to try again?  {reset}'.format(
                yellow=ANSI_YEL, reset=ANSI_RESET))
            if not retry:
                if AQ or CO2 or Weather:
                    cont = ques_conv('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET))
                    if not cont:
                        AQ, CO2, Weather = False, False, False
                        AQ_data, CO2_data, weather_data = None, None, None
                        testing = False
                        break
                testing = False
            else:
                change_int = ques_conv('{yellow}Would you like to change the time interval?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET))
                if change_int:
                    interval_new = ques_conv(INTERVAL_QUESTION, True)
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
    print(DOUBLE_BREAK_LINE)
if AQ:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing, interval_new, average_data = True, True, None, []
    while testing:
        ind_err = False
        if first_run:
            print(running.format(sensor_name=names[1], interval=interval))
            first_run = False
        else:
            print('\n')
            if interval_new != None:
                print(retrying.format(sensor_name=names[1], interval=interval_new))
            else:
                print(retrying.format(sensor_name=names[1], interval=interval))
        try:
            average_data = sensor_AQ.handle_data(start_time, end_time, None)
        except IndexError:
            print(('{red}Index Error from the Air Quality Sensor. \n{reset}' +
                '{red}This happens if the sensor was run too quickly after restart or if the \n{reset}' +
                '{red}Air Quality sensor is not sending signals to the RaspberryPi.\n{reset}' +
                '{red}Make sure the AQ sensor is connected and try again.\n{reset}' +
                '{red}If this continues, try restarting or checking the PiHat.{reset}').format(
                red=ANSI_RED, reset=ANSI_RESET))
            ind_err = True
        except ZeroDivisionError:
            print(('{red}ZeroDivisionError from the Air Quality Sensor. \n{reset}' +
                '{red}This happens if the sensor was run too quickly after restart or if the \n{reset}' +
                '{red}Air Quality sensor is not sending signals to the RaspberryPi.\n{reset}' +
                '{red}Make sure the AQ sensor is connected and try again.\n{reset}' +
                '{red}If this continues, try restarting or checking the PiHat.{reset}').format(
                red=ANSI_RED, reset=ANSI_RESET))
            ind_err = True
        except serial.serialutil.SerialException:
            print(('{red}SerialException error from the Air Quality Sensor. \n{reset}' +
                '{red}This happens if the Air Quality Sensor is already running through some other \n{reset}' +
                '{red}process on the device such as main.sh running the AQ.sh script which in turn runs\n{reset}' +
                '{red}its own incident of the AQ manager. Since the Air Quality sensor uses the serial {reset}' +
                '{red}port,\n then only one process can access that port. So shut down any other {reset}' +
                '{red}process that is running the Air Quality sensor and try again.{reset}').format(
                red=ANSI_RED, reset=ANSI_RESET))
        if any(data != 0 for data in average_data) and not ind_err:
            AQ_data = True
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[1]))
            for i in range(3):
                print(AQ_PM_DISPLAY_TEXT.format(variable=AQ_VARIABLES[i], avg_data=average_data[i]))
            for i in range(3, 9):
                print(AQ_P_DISPLAY_TEXT.format(variable=AQ_VARIABLES[i], avg_data=average_data[i]))
            testing = False
        else:
            if not ind_err:
                print('{red}No data found from the {sensor}!{reset}'.format(
                    red=ANSI_RED, reset=ANSI_RESET, sensor=names[1]))
                print(('{red}Either the interval was too short, the sensor is not connected or no data\n{reset}' +
                    '{red}was found. Make sure the sensor is connected and try again to determine\n{reset}' +
                    '{red}whether it is the circuit or not.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))
            print('\n')
            retry = ques_conv('{yellow}Would you like to try again?  {reset}'.format(
                yellow=ANSI_YEL, reset=ANSI_RESET))
            if not retry:
                if CO2 or Weather:
                    cont = ques_conv('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                        yellow=ANSI_YEL, reset=ANSI_RESET))
                    if not cont:
                        CO2, Weather = False, False
                        CO2_data, weather_data = None, None
                        testing = False
                        break
                testing = False
            else:
                change_int = ques_conv('{yellow}Would you like to change the time interval?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET))
                if change_int:
                    interval_new = ques_conv(INTERVAL_QUESTION, True)
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
    print(DOUBLE_BREAK_LINE)
if CO2:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing, interval_new, average_data = True, True, None, []
    while testing:
        neg_conc = False
        if first_run:
            print(running.format(sensor_name=names[2], interval=interval))
            first_run = False
        else:
            print('\n')
            if interval_new != None:
                print(retrying.format(sensor_name=names[2], interval=interval_new))
            else:
                print(retrying.format(sensor_name=names[2], interval=interval))
        average_data = sensor_CO2.handle_data(start_time, end_time, None)
        if average_data[0] > 0:
            CO2_data = True
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[2]))
            for i in range(len(CO2_VARIABLES)):
                print(CO2_DISPLAY_TEXT.format(variable=CO2_VARIABLES[i], data=average_data[i]))
            testing = False
            break
        elif average_data[0] < 0:
            print(('{red}Found negative data from the CO2 Sensor. \n{reset}' +
                '{red}This usually means that the CO2 Sensor is not actually connected.\n{reset}' +
                '{red}Make sure the CO2 sensor is connected then try again.\n{reset}' +
                '{red}If this continues, it is likely a problem with the PiHat{reset}').format(
                red=ANSI_RED, reset=ANSI_RESET))
            neg_conc = True
        else:
            print('{red}No data found from the {sensor}!{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET, sensor=names[2]))
            print(('{red}Either the interval was too short, the sensor is not connected or no data\n{reset}' +
                '{red}was found. Make sure the sensor is connected and try again to determine\n{reset}' +
                '{red}whether it is the circuit or not.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))
        print('\n')
        retry = ques_conv('{yellow}Would you like to try again?  {reset}'.format(
            yellow=ANSI_YEL, reset=ANSI_RESET))
        if not retry:
            if Weather:
                cont = ques_conv('{yellow}Would you like to continue to other sensors?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET))
                if not cont:
                    Weather, weather_data = False, None
                    testing = False
                    break
            testing = False
        else:
            change_int = ques_conv('{yellow}Would you like to change the time interval?  {reset}'.format(
                yellow=ANSI_YEL, reset=ANSI_RESET))
            if change_int:
                interval_new = ques_conv(INTERVAL_QUESTION, True)
                start_time, end_time = time.time(), time.time() + interval_new
            else:
                start_time, end_time = time.time(), time.time() + interval
    print(DOUBLE_BREAK_LINE)
if Weather:
    start_time, end_time = time.time(), time.time() + interval
    first_run, testing, interval_new, average_data = True, True, None, []
    while testing:
        if first_run:
            print(running.format(sensor_name=names[3], interval=interval))
            first_run = False
        else:
            print('\n')
            if interval_new != None:
                print(retrying.format(sensor_name=names[3], interval=interval_new))
            else:
                print(retrying.format(sensor_name=names[3], interval=interval))
        average_data = sensor_weather.handle_data(start_time, end_time, None)
        if any(data != 0 for data in average_data):
            weather_data = True
            print('{green}Found data from the {sensor}!{reset}'.format(
                green=ANSI_GR, reset=ANSI_RESET, sensor=names[3]))
            for i in range(len(WEATHER_VARIABLES)):
                print(WEATHER_DISPLAY_TEXT.format(
                    variable=WEATHER_VARIABLES[i], unit=WEATHER_VARIABLES_UNITS[i], data=average_data[i]))
            testing = False
        else:
            print('{red}No data found from the {sensor}!{reset}'.format(
                red=ANSI_RED, reset=ANSI_RESET, sensor=names[3]))
            print(('{red}Either the interval was too short, the sensor is not connected or no data\n{reset}' +
                '{red}was found. Make sure the sensor is connected and try again to determine\n{reset}' +
                '{red}whether it is the circuit or not.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))
            print('\n')
            retry = ques_conv('{yellow}Would you like to try again?  {reset}'.format(
                yellow=ANSI_YEL, reset=ANSI_RESET))
            if not retry:
                testing = False
                break
            else:
                change_int = ques_conv('{yellow}Would you like to change the time interval?  {reset}'.format(
                    yellow=ANSI_YEL, reset=ANSI_RESET))
                if change_int:
                    interval_new = ques_conv(INTERVAL_QUESTION, True)
                    start_time, end_time = time.time(), time.time() + interval_new
                else:
                    start_time, end_time = time.time(), time.time() + interval
    print(SINGLE_BREAK_LINE)
init_letters, letters, final = ['p', 'a', 'c', 'w'], [], []
sensors_data = {'p':pocket_data, 'a':AQ_data, 'c':CO2_data, 'w':weather_data}
sensors_data_true = {k:v for k,v in sensors_data.items() if v != None}
for k,v in sensors_data_true.items():
    letters.append(k)
    final.append(v)
for i in range(len(letters)):
    for j in range(len(init_letters)):
        if letters[i] == init_letters[j]:
            if final[i]:
                print(('{green}Successful data acquisition from the {sensor}!{reset}').format(
                    green=ANSI_GR, sensor=names[j], reset=ANSI_RESET))
            else:
                print(('{red}Unsuccessful data acquisition from the {sensor}.{reset}').format(
                    red=ANSI_RED, sensor=names[j], reset=ANSI_RESET))
if any(ans == False for ans in final):
    print(('{red}At least one of the sensors did not acquire data properly!\n{reset}' +
        '{red}Check back on error messages for possible fixes.{reset}').format(red=ANSI_RED, reset=ANSI_RESET))
else:
    print(('{green}All the sensors aquired data properly!\n{reset}' +
        '{green}The tested PiHat should be good to go!{reset}').format(green=ANSI_GR, reset=ANSI_RESET))
print(SINGLE_BREAK_LINE)
#Turning off LEDs becuase otherwise they would stay on from the manager initializations.
if pocket:
    sensor_pocket.network_LED.stop_blink()
    sensor_pocket.counts_LED.stop_blink()
    sensor_pocket.network_LED.off()
    sensor_pocket.counts_LED.off()
