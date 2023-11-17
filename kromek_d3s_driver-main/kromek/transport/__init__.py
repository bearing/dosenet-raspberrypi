import logging
from .transport import Transport, Connection

_transport_types = {}

# try:
#    from ._bluetooth import BluetoothTransport
#    _transport_types['bluetooth'] = BluetoothTransport
# except ImportError as e:
#    logging.debug('Failed to import bluetooth.  %s', e)

try:
    from ._serial import UsbSerialTransport

    _transport_types["serial"] = UsbSerialTransport
except ImportError as e:
    logging.debug("Failed to import serial.  %s", e)

try:
    from ._usb import UsbTransport

    _transport_types["usb"] = UsbTransport
except ImportError as e:
    logging.debug("Failed to import USB.  %s", e)

if len(_transport_types) <= 0:
    raise ImportError("No transports available")


def get_transport(transport_type):
    if transport_type in _transport_types:
        return _transport_types[transport_type]
    return None


def discover(transport_type=None):
    ret = []
    if transport_type is None:
        transport_type = list(_transport_types.keys())
    else:
        transport_type = [transport_type]

    for tt in transport_type:
        if tt in _transport_types:
            trans = _transport_types[tt]()
            for d in trans.discover():
                d += (trans,)
                ret.append(d)
    return ret


def connect(device, transport=None):
    if transport is None:
        trans = device[-1]
    else:
        if type(transport) == str:
            transport = get_transport(transport)
        trans = transport
    return trans.connect(device)


__all__ = [
    "Transport",
    "Connection",
    "get_transport",
    "discover",
    "connect",
]
