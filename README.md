# Berkeley DoseNet Raspberry-Pi 
Raspberry Pi specific software for devices.
___
### Please take note
This readme file may not be fully up to date. (*Last updated: 6/22/18*)
___
### Running the Devices
Make sure that you are in the proper directory with `cd ~/dosenet-raspberrypi/` (Otherwise the files won't run!)

		main.sh
> **Usage:**
>> `sudo bash main.sh start`
> 
> Runs all the sensors with all default running settings (*i.e* 5 min interval, data-logging off, etc.)
>
>> `sudo bash main.sh test`
>
> Runs all the sensors in test mode (*i.e* 30 sec interval, data-logging on, etc.)
>
>> `sudo bash main.sh stop`
>
> Stops the main.sh script and all subprocesses from running

If however, you wanted to run an individual sensor instead of the whole set of them at once then you will want to use:

		managers.py
> **Usage:**
>> `python managers.py --sensor (sensor #)`
> 
> Where the sensor # is specific to the sensor you want to use. There are also general and specific inputs that you can use when running this program, 
> for example, if you wanted to specify the interval you would add `--interval (time in seconds)` or `-i (time in seconds)`. So if you wanted to run
> the Air Quality sensor for 30 second intervals, you would enter: `python managers.py --sensor 3 --interval 30` For running a specific sensor, the different sensor numbers are:
> 
> **1 for Pocket Geiger / 2 for D3S / 3 for Air Quality / 4 for CO2 / 5 for Weather**

There are also other options that can be manipulated through entering arguments at execution of the `managers.py` file. See below for a table containing all the options that 
can be entered in the same fashion as choosing an interval.
 
For any of the below arguments, they can be replaced by their shortcuts. i.e running:
	
		python managers.py --sensor 1
		
Is the same thing as running:
		
		python managers.py -s 1
		
**Important Note:** The sensor argument is the only *required* argument

In regards to the example usages, replace anything in parentheses with the desired value: `--interval (time in seconds)` at 30 seconds would be `--interval 30`
Also any argument who's default is False without a parenthesis next to the example usage option will automatically get set to True if the argument is used. 
For example, calling test with `--test` will store the test variable as True in the execution of the `managers.py` program.

**Second Important Note:** Only the sensor argument is required, all the rest are set automatically if not used

|  Argument   | Short Cut | Example Usage | Defaults |
|-------------|:---------:|---------------|:--------:|
|`--sensor`|`-s`|`python managers.py --sensor (sensor #)`|`None`|
|`--interval`|`-i`|`python managers.py -s (#) --interval (time in seconds)`|`300`|
|`--config`|`-c`|`python managers.py -s (#) --config (path to config file)`|`'/home/pi/config/config.csv'`|
|`--publickey`|`-k`|`python managers.py -s (#) --publickey (path to publickey file)`|`'/home/pi/config/id_rsa_lbl.pub'`|
|`--hostname`|`-4`|`python managers.py -s (#) --hostname (hostname server)`|`'dosenet.dhcp.lbl.gov'`|
|`--port`|`-p`|`python managers.py -s (#) --port (port #)`|For UDP:`5005`, For TCP:`5100`|
|`--test`|`-t`|`python managers.py -s (#) --test`|`False`|
|`--verbosity`|`-v`|`python managers.py -s (#) --verbosity (verbosity value)`|`1`|
|`--log`|`-l`|`python managers.py -s (#) --log`|`False`|
|`--logfile`|`-g`|`python managers.py -s (#) --logfile (path to logfile)`|`'/home/pi/debug.log_(sensor name)'`|
|`--datalogflag`|`-d`|`python managers.py -s (#) --datalogflag`|`False`|
|`--datalog`|`-f`|`python managers.py -s (#) --datalog (path to datalogfile)`|`'/home/pi/data-log_(sensor name).txt'`|
|`--sender-mode`|`-m`|`python managers.py -s (#) --sender-mode (sender-mode type)`|`'tcp'`|
|`--aeskey`|`-q`|`python managers.py -s (#) --aeskey (path to aeskey file)`|`'/home/pi/config/secret.aes'` (for D3S)|

Pocket Geiger (*Sensor #1*) specific varibles that can be entered are:

|  Argument   | Short Cut | Example Usage | Defaults |
|-------------|:---------:|---------------|:--------:|
|`--counts_LED_pin`|`-o`|`python managers.py -s 1 --counts_LED_pin (pin #)`|new:`19`, old:`21`|
|`--network_LED_pin`|`-e`|`python managers.py -s 1 --network_LED_pin (pin #)`|new:`16`, old:`20`|
|`--noise_pin`|`-n`|`python managers.py -s 1 --noise_pin (pin #)`|`4`|
|`--signal_pin`|`-u`|`python managers.py -s 1 --signal_pin (pin #)`|`17`|

D3S (*Sensor #2*) specific variables that can be entered are:

|  Argument   | Short Cut | Example Usage | Defaults |
|-------------|:---------:|---------------|:--------:|
|`--calibrationlog`|`-j`|`python managers.py -s 2 --calibrationlog (path to calibrationlog file)`|`'/home/pi/calibration-log_D3S.txt'`|
|`--calibrationlogflag`|`-z`|`python managers.py -s 2 --calibrationlogflag`|`False`|
|`--calibrationlogtime`|`-x`|`python managers.py -s 2 --calibrationlogtime (time in seconds)`|`600`|
|`--count`|`-0`|`python managers.py -s 2 --count (count #)`|`0`|
|`--d3s_LED_pin`|`-3`|`python managers.py -s 2 --d3s_LED_pin (pin #)`|new:`13`, old:`19`|
|`--d3s_LED_blink`|`-b`|`python managers.py -s 2 --d3s_LED_blink (blink True/False)`|`True`|
|`--d3s_LED_blink_period_1`|`-1`|`python managers.py -s 2 --d3s_LED_blink_period_1 (time in seconds)`|`0.75`|
|`--d3s_LED_blink_period_2`|`-2`|`python managers.py -s 2 --d3s_LED_blink_period_2 (time in seconds)`|`0.325`|
|`--d3s_light_switch`|`-u`|`python managers.py -s 2 --d3s_light_switch (True/False)`|`False`|
|`--device`|`-e`|`python managers.py -s 2 --device (all or specific D3S)`|`'all'`|
|`--log-bytes`|`-y`|`python managers.py -s 2 --log-bytes`|`False`|
|`--transport`|`-n`|`python managers.py -s 2 --transport (transport type)`|`'usb'`|

Air Quality Sensor (*Sensor #3*) specific varibles that can be entered are:

|  Argument   | Short Cut | Example Usage | Defaults |
|-------------|:---------:|---------------|:--------:|
|`--AQ_port`|`-a`|`python managers.py -s 3 --AQ_port (a Serial version of a port)`|`DEFAULT_AQ_PORT` (see `globalvalues.py`)|

CO2 Sensor (*Sensor #4*) specific varibles that can be entered are:

|  Argument   | Short Cut | Example Usage | Defaults |
|-------------|:---------:|---------------|:--------:|
|`--CO2_port`|`-a`|`python managers.py -s 4 --CO2_port (a port using Adafruit_MCP3008 package)`|`DEFAULT_CO2_PORT` (see `globalvalues.py`)|

Weather Sensor (*Sensor #5*) specific varibles that can be entered are:

|  Argument   | Short Cut | Example Usage | Defaults |
|-------------|:---------:|---------------|:--------:|
|`--Weather_Port`|`-a`|`python managers.py -s 5 --Weather_Port (a port using Adafruit_BME280 package)`|`DEFAULT_WEATHER_PORT` (see `globalvalues.py`)|
