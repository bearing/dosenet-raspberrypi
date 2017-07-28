#! /bin/sh
dose_net_dir=/home/pi/dosenet-raspberrypi

for i in $@
do
  echo {i}
  case {i} in 
    AQ)
      echo "Starting Air Quality Sensor"
      sudo python $dose_net_dir/air_quality_test.py
      ;;

    ADC)
      echo "Starting CO2 Sensor and UV Sensor"
      sudo python $dose_net_dir/adc_test.py
      ;;

    AT)
      echo "Starting Atmosphere Sensor"
      sudo python $dose_net_dir/weather_test.py
      ;;

    Si)
      echo "Starting Silicon Radiation Detector" > /tmp/pocket_manager.log
      sudo python $dose_net_dir/manager.py --logfile /tmp/pocket_manager.log >>/tmp/pocket_manager.log 2>&1
      ;;

    CsI)
      echo "Starting Cesium Iodide Radiation Detector" > /tmp/d3s_manager.log
      sudo python $dose_net_dir/manager_D3S.py --logfile /tmp/d3s_manager.log >> /tmp/d3s_manager.log 2>&1
      ;;

    *)
      echo "Error: Incorrect Usage"
      echo "Usage: /home/pi/dosenet-raspberrypi/SensorTest.sh {AQ|AT|ADC|Si|CsI}"
      exit 1
      ;;

  esac
done
exit 0
