import bluetooth
from kromek.protocol import BufferUnderflowError
from kromek.transport.transport import Transport, Connection


class BluetoothConnection(Connection):
    def __init__(self, device):
        self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._sock.connect((device[0], 5))
        self._sock.setblocking(False)

    def _send(self, message):
        data = message.write()
        self._sock.send(data)

    def _recv(self, message):
        buf = ""
        # Read until we have enough bytes for the message
        while True:
            try:
                buf += self._sock.recv(1024)
            except bluetooth.BluetoothError:
                continue
            try:
                message.read(buf)
            except BufferUnderflowError:
                continue
            return message

    def close(self):
        self._sock.close()


class BluetoothTransport(Transport):
    def discover(self):
        ret = []
        devs = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
        for d in devs:
            if "55:33:" == d[0][0:6]:
                ret.append(d)
        return ret

    def connect(self, device):
        return BluetoothConnection(device)
