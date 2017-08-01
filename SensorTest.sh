#! /bin/sh
dose_net_dir=/home/pi/dosenet-raspberrypi

for i in $@
do
  case $i in
    AQ)
      echo "Starting Air Quality Sensor"
      sudo python $dose_net_dir/air_quality_test.py &
      ;;

    ADC)
      echo "Starting CO2 Sensor and UV Sensor"
      sudo python $dose_net_dir/adc_test.py &
      ;;

    AT)
      echo "Starting Atmosphere Sensor"
      sudo python $dose_net_dir/weather_test.py &
      ;;

    Si)
      echo "Starting Silicon Radiation Detector" > /tmp/pocket_manager.log
      sudo python $dose_net_dir/manager.py --logfile /tmp/pocket_manager.log >>/tmp/pocket_manager.log 2>&1
      ;;

    CsI)
      echo "Starting Cesium Iodide Radiation Detector" > /tmp/d3s_manager.log
      sudo python $dose_net_dir/manager_D3S.py --logfile /tmp/d3s_manager.log >> /tmp/d3s_manager.log 2>&1
      ;;

    stop)
      echo "Stopping Sensor Programs."
      sudo pkill -SIGTERM -f manager.py
      sudo pkill -SIGTERM -f air_quality_test.py
      sudo pkill -SIGTERM -f manager_D3S.py
      sudo pkill -SIGTERM -f weather_test.py
      sudo pkill -SIGTERM -f adc_test.py
      exit 0
      ;;

    *)
      echo "Error: Incorrect Usage"
      echo "Usage: /home/pi/dosenet-raspberrypi/SensorTest.sh {AQ|AT|ADC|Si|CsI|Stop}"
      exit 1
      ;;

  esac
done
exit 0
