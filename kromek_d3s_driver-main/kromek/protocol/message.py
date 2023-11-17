import struct
from ..protocol import Component, MessageType, ErrorCode


def _create_request_response(type, message):
    if type == MessageType.GET_16BIT_SPECTRUM:
        return Get16BitSpectrum(message), Get16BitSpectrum(message)
    if type == MessageType.GET_BIAS or type == MessageType.SET_BIAS:
        return GetSetBias(message), GetSetBias(message)
    if type == MessageType.GET_GAIN or type == MessageType.SET_GAIN:
        return GetSetGain(message), GetSetGain(message)
    if type == MessageType.GET_LLD or type == MessageType.SET_LLD:
        return GetSetLLD(), GetSetLLD()
    if type == MessageType.GET_SERIAL_NO:
        return GetSerial(message), GetSerial(message)
    if type == MessageType.INITIALIZE:
        return Initialize(message), Initialize(message)
    if type == MessageType.GET_STATUS:
        return GetStatus(message), GetStatus(message)
    return None, None


class BufferUnderflowError(Exception):
    """I/O operation failed."""

    def __init__(self, *args, **kwargs):
        super(BufferUnderflowError, self).__init__(args, kwargs)


class ProtocolError(Exception):
    """I/O operation failed."""

    def __init__(self, code, msg):
        super(ProtocolError, self).__init__(msg)
        self._code = code

    def is_recoverable(self):
        return ErrorCode.is_recoverable(self._code)


class Message(object):
    """
    Base class for a kromek protocol request/response
    """

    def __init__(self, type=None, component=None):
        self._type = type
        self._component = component
        self._sequence = 0
        self._crc = 0
        self._length = 0
        self._request, self._response = _create_request_response(type, self)

    def write(self):
        """
        Write the message and return the buffer
        :return: A buffer for sending
        """
        out = bytearray()
        out += struct.pack("b", self._sequence)
        out += struct.pack("b", self._component)
        out += struct.pack("B", self._type)
        # print("OUT")
        # print(repr(out))
        out.extend(self._write())
        out += struct.pack("<h", self._crc)
        out = struct.pack("<h", len(out) + 2) + out
        hexstr = "".join("{:02x}".format(x) for x in out)
        print("REQ -> {0}".format(hexstr))
        return out

    def read(self, buf):
        """
        Read the message from the buffer
        :param buf: the buf to read from
        :return: self
        """
        buflen = len(buf)
        if buflen < 2:
            raise BufferUnderflowError("Buffer too small")
        self._length = struct.unpack("<H", buf[0:2])[0]
        if self._length < buflen:
            raise BufferUnderflowError(
                "Buffer too large. Got %s expect %s." % (buflen, self._length)
            )
        if buflen < self._length:
            raise BufferUnderflowError(
                "Buffer too small. Got %s expect %s." % (buflen, self._length)
            )
        # print 'REP <- %s' %buf.encode('hex')
        # print(type(buf))
        # print(repr(buf))
        self._sequence = buf[2]
        self._component = buf[3]
        self._type = buf[4]

        if self._type == MessageType.ERROR:
            err = buf[5]
            msg = Response.read_null_term_ascii(buf[6:])
            raise ProtocolError(err, msg)

        # just in case
        if self._response is None:
            self._request, self._response = _create_request_response(self._type, self)
        self._read(buf[5:])
        return self

    def _write(self):
        """
        Write the meat of the message
        :return: a buffer
        """
        if self._request is not None:
            return self._request.write(self)
        return bytearray()

    def _read(self, buf):
        """
        Read the meat of a message
        :return: a buffer
        """
        if self._response is not None:
            self._response.read(self, buf)


class Request(object):
    """
    Composable part of a message that can serialize a request
    """

    def write(self, message):
        return bytearray()


class Response(object):
    """
    Composable part of a message that can serialize a response
    """

    def read(self, message, buf):
        pass

    @classmethod
    def read_null_term_ascii(cls, buf):
        adv = 0
        ret = bytearray()
        for c in buf:
            if c == 0:
                break
            ret += struct.pack("b", c)
            adv += 1
        return ret, adv


class Initialize(Request, Response):
    def __init__(self, message):
        message._component = Component.INTERFACE_BOARD

    def read(self, message, buf):
        message.firmware_version = struct.unpack("<H", buf[0:2])[0]
        message.response_message, adv = Response.read_null_term_ascii(buf[2:])


class GetSerial(Request, Response):
    def __init__(self, message):
        message._component = Component.INTERFACE_BOARD

    def read(self, message, buf):
        serial_bytes, adv = Response.read_null_term_ascii(buf)
        message.serial = serial_bytes.decode("ascii")


class GetStatus(Request, Response):
    def __init__(self, message):
        message._component = Component.INTERFACE_BOARD

    def read(self, message, buf):
        message.status = buf[0]
        message.power = buf[1]
        message.temperature = buf[2]
        message.sigmaStatus = buf[3]
        message.tn15Status = buf[4]
        message.batteryLevel = buf[5]
        message.batteryChargeRate = buf[6]
        message.batteryTemperature = buf[7]
        # usbStatus = buf[8]
        # bluetoothStatus = buf[9]


class GetSetBias(Request, Response):
    def __init__(self, message):
        message._component = Component.GAMMA_DETECTOR

    def write(self, message):
        try:
            return struct.pack("<H", message.bias)
        except AttributeError:
            pass
        return ""

    def read(self, message, buf):
        message.bias = struct.unpack("<H", buf[0:2])[0]


class GetSetGain(Request, Response):
    def __init__(self, message):
        message._component = Component.GAMMA_DETECTOR

    def write(self, message):
        try:
            return struct.pack("B", message.gain)
        except AttributeError:
            pass
        return ""

    def read(self, message, buf):
        message.gain = buf[0]


class GetSetLLD(Request, Response):
    def write(self, message):
        try:
            return struct.pack("<H", message.lld)
        except AttributeError:
            pass
        return ""

    def read(self, message, buf):
        message.lld = struct.unpack("<H", buf[0:2])[0]


class Get16BitSpectrum(Request, Response):
    def __init__(self, message):
        message._component = Component.INTERFACE_BOARD
        message.time = 0
        message.neutron_count = 0
        message.spectrum = [0] * 512

    def read(self, message, buf):
        message.time = struct.unpack_from("<i", buf, 0)[0]
        message.neutron_count = struct.unpack_from("<H", buf, 4)[0]
        message.spectrum = [0] * 4096
        off = 6
        for i in range(4096):
            message.spectrum[i] += struct.unpack_from("<H", buf, off)[0]
            off += 2
