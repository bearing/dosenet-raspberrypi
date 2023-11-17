# Kromek D3S Driver

This repository was adapted from the following [repository](https://github.com/lbl-anp/radmon_d3s). It provides the barebone code to be able to connect to and read from a Kromek D3S detector.

## Connect via USB as a non-root user on Linux
1. Execute the shell script:
```bash
sudo sh startup/initenv.sh
```
2. If the detector is connected, disconnect it and reconnect it.
3. You should now be able to connect to the detector without sudo.

## Create a Conda environment from a YML file
To create a Conda environment to connect to and read from a Kromek D3S detector, navigate to the root of this repository from the terminal and enter the following commands:
```bash
conda env create -f environment.yml
conda activate kromek_d3s_driver
```

## Connect to and read from a Kromek D3S detector
From the root of this repository, enter the following command:
```bash
python3 capture.py
```
Note: Depending on your environment, the above command may need to be preceded by `sudo`.  
