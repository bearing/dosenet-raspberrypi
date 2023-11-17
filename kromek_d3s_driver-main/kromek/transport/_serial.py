import re
import os
import serial
import time

from ..protocol import BufferUnderflowError
from ..transport.transport import Transport, Connection

_patterns = [r"/dev/ttyACM[\d]?", r"/dev/ttyUSB[\d]?", r"/dev/tty.usbmodem[\d]+"]

class UsbSerialConnection(Connection):
    def __init__(self, path):
        self._conn = serial.Serial(
            path,
            115200,
            serial.EIGHTBITS,
            serial.PARITY_NONE,
            serial.STOPBITS_ONE,
            0.001,
        )

    def _send(self, message):
        data = message.write()
        written = 0
        total = len(data)
        while written < total:
            written += self._conn.write(data[written:])

    def _recv(self, message):
        buf = b""
        # Read until we have enough bytes for the message
        while True:
            ready = self._conn.inWaiting()
            while ready <= 0:
                time.sleep(0.01)
                ready = self._conn.inWaiting()
                continue
            buf += self._conn.read()
            if buf == b'\x00':
                return None
            try:
                message.read(buf)
            except BufferUnderflowError:
                continue
            return message

    def close(self):
        self._conn.close()


class UsbSerialTransport(Transport):
    def discover(self):
        ret = []
        for dev_file in os.listdir("/dev"):
            path = "/dev/%s" % dev_file
            for pattern in _patterns:
                if re.search(pattern, path):
                    ret.append((str(path),))
                    break
        return ret

    def connect(self, device):
        dev = device[0]

        # is this a serial tty device?
        if type(dev) == str:
            for pattern in _patterns:
                if re.search(pattern, dev) is not None:
                    return UsbSerialConnection(dev)

        return None
