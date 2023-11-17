#!/usr/bin/env python3

import kromek
import TimerLoop
import datetime
import traceback

base_config = {
    "upload_period": 10,
    # "config_check_period": 7200,
    # "ping_period": 900,
    "tick_length": 0.5,
    # "sensor_params": {},
    # "max_consec_net_errs": 10,
    # "mail_check_period": 7200,
    # "bground_check_period": 5,
}


def pre_run():
    kdevs = kromek.discover()
    print(f"Discovered {kdevs}")
    if len(kdevs) <= 0:
        print("Exiting early, no devices found!")
        return

    try:
        kconn = kromek.connect(kdevs[0])
        if len(kdevs) > 1:
            print("Multiple devices found! Checking for kromek device")
            for dev in kdevs:
                ikconn = kromek.connect(dev)
                res = check_sensor(ikconn)
                print(res)
                if bool(res):
                    kconn = ikconn
                    print("Kromek device found at", kconn)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return

    cfg = {k: base_config[k] for k in base_config}
    cfg["kconn"] = kconn

    return cfg

def check_sensor(conn):
    res = kromek.get_value(conn, param="status")
    return res

'''
def check_sensor(cfg):
    res = kromek.get_value(cfg["kconn"], param="status")
    return res
'''

def read_sensor(cfg):
    print("read_sensor()")
    fake_kromek = False

    sdata = {}
    if fake_kromek:
        sdata = {
            "serial": "blee blop",
            "bias": 123,
            "measurement": [1, 2, 3, 4, 5, 6, 7],
        }
    else:
        for group in [
            "serial",
            "status",
            "measurement",
            "gain",
            "bias",
            "lld-g",
            "lld-n",
        ]:
            res = kromek.get_value(cfg["kconn"], param=group)

            """
            Gets the timestamp for the measurement. 
            This parameter could be added to the Kromek package.
            """
            if group == "measurement":
                res["timestamp"] = datetime.datetime.now()

            for k in res:
                sdata[k] = res[k]
    return sdata


class CapHandlers(object):
    def __init__(self, cfg):
        self.cfg = cfg

    def take_reading(self, name, now):
        sdata = read_sensor(self.cfg)
        print(sdata)
        return False


def main(cfg):
    ch = CapHandlers(cfg)
    te = TimerLoop.TimerLoop()

    te.addHandler(ch.take_reading, cfg["upload_period"])
    te.run(cfg["tick_length"])


if __name__ == "__main__":
    try:
        cfg = pre_run()
        if cfg:
            main(cfg)
    except Exception as e:
        print("Whoops!", e)
