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
> the Air Quality sensor for 30 second intervals, you would enter: `python managers.py --sensor 3 --interval 30` See below for a table containing all the 
> options that can be entered in the same fashion as choosing an interval. 
> 

For any of the below arguments, they can be replaced by their shortcuts. i.e running:
	
		python managers.py --sensor 1
		
Is the same thing as running:
		
		python managers.py -s 1
		
**Important Note:** The sensor argument is the only *required* argument

In regards to the example usages, replace anything in parentheses with the desired value: `--interval (time in seconds)` at 30 seconds would be `--interval 30`

| Argument | Short Cut | Example Usage | Defaults |
|----------|:---------:|---------------|:--------:|
|--sensor|-s|`python managers.py --sensor (sensor #)`|None|
|--interval|-i|`python managers.py --interval (time in seconds)`|500|
|--config|-c|`python managers.py --config (path to config file)`|'/home/pi/config/config.csv'|
|--publickey|-k|`python managers.py --publickey (path to publickey file)`|'/home/pi/config/id\_rsa_lbl.pub'|
|--hostname|-4|`python managers.py --hostname (hostname server)`|'dosenet.dhcp.lbl.gov'|
|--port|-p|`python managers.py --port (port #)`|For UDP:5005, For TCP:5100|