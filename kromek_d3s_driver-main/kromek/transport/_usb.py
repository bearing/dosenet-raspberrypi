import os
import struct
from usb1 import (
    USBContext,
    # USBDevice,
    # USBDeviceHandle,
    # USBEndpoint,
    # USBInterface,
    USBError,
)
from ..protocol import BufferUnderflowError
from ..transport.transport import Transport, Connection


def _find_tty_for_device(vendor_id, product_id=None, frm="/sys/devices/pci0000:00"):
    for name in os.listdir(frm):
        if name in frm:
            continue
        full_path = frm + os.path.sep + name
        if "ttyACM" == name[0:6] or "ttyUSB" == name[0:6]:
            path = full_path + os.path.sep + "device" + os.path.sep + "uevent"
            if os.path.exists(path):
                with open(path) as d:
                    for line in d.readlines():
                        ids = line.split("=")[1].split("/")
                        if len(ids) >= 2:
                            vendor = struct.unpack(">H", ids[0].zfill(4).decode("hex"))[
                                0
                            ]
                            product = struct.unpack(
                                ">H", ids[1].zfill(4).decode("hex")
                            )[0]
                            if vendor_id == vendor and (
                                product_id is None or product_id == product
                            ):
                                print("/dev/" + name)
        elif os.path.isdir(full_path):
            path = _find_tty_for_device(vendor_id, product_id, full_path)
            if path is not None:
                return path
    return None


class UsbCdcAcmConnection(Connection):
    def __init__(self, devstr):
        self._dev = None
        self._data_out = None
        self._data_in = None
        self._ctx = USBContext()
        for device in self._ctx.getDeviceList():
            if devstr == str(device):
                self._dev = device
                break

        if self._dev is None:
            raise RuntimeError("Failed to find %s", devstr)

        self._usb_handle = self._dev.open()
        for iface in self._dev.iterSettings():
            iface_num = iface.getNumber()
            if iface_num in (0, 1):
                if self._usb_handle.kernelDriverActive(iface_num):
                    self._usb_handle.detachKernelDriver(iface_num)
                self._usb_handle.claimInterface(iface_num)
                if iface_num == 1:
                    self._data_out = iface[1].getAddress()
                    self._data_in = iface[0].getAddress()

        if self._data_in is None or self._data_out is None:
            raise RuntimeError("Failed to find bulk transfer for %s", devstr)

        # config = self._dev.get_active_configuration()
        # self.control_iface = config[(0, 0)]
        # self.data_iface = config[(1, 0)]

        # self.control_out = usb.util.find_descriptor(
        #     self.control_iface,
        #     custom_match=lambda e: endpoint_direction(e.bEndpointAddress)
        #     == ENDPOINT_OUT,
        # )
        # self.control_in = usb.util.find_descriptor(
        #     self.control_iface,
        #     custom_match=lambda e: endpoint_direction(e.bEndpointAddress)
        #     == ENDPOINT_IN,
        # )

        # self.data_out = usb.util.find_descriptor(
        #     self.data_iface,
        #     custom_match=lambda e: endpoint_direction(e.bEndpointAddress)
        #     == ENDPOINT_OUT,
        # )
        # self.data_in = usb.util.find_descriptor(
        #     self.data_iface,
        #     custom_match=lambda e: endpoint_direction(e.bEndpointAddress)
        #     == ENDPOINT_IN,
        # )

        self._init(115200, 8, 0, 0)

    def _init(self, baud_rate, data_bits, stop_bits, parity):
        msg = struct.pack("<IBBB", baud_rate, stop_bits, data_bits, parity)
        self._usb_handle.controlWrite(0x20 | 0x01, 0x20, 0, 0, msg)

    def _send(self, message):
        data = message.write()
        self._usb_handle.bulkWrite(self._data_out, data, 1000)

    def _recv(self, message):
        buf = b""
        # Read until we have enough bytes for the message
        while True:
            try:
                buf += self._usb_handle.bulkRead(self._data_in, 8192, 1000)
            except USBError as err:
                if hasattr(err, "value") and err.value == -7:
                    continue
                if hasattr(err, "errno") or err.errno == 110:
                    continue
                raise err
            try:
                message.read(buf)
            except BufferUnderflowError:
                continue
            return message

    def close(self):
        if self._usb_handle is not None:
            self._usb_handle.close()
        if self._ctx is not None:
            self._ctx.exit()


class UsbTransport(Transport):
    def discover(self):
        ret = []
        ctx = USBContext()
        try:
            for device in ctx.getDeviceList():
                vid = device.getVendorID()
                if vid == 1240 or vid == 1155 or vid == 10842:
                    ret.append((str(device),))
        finally:
            ctx.exit()
        return ret

    def connect(self, device):
        dev = device[0]
        return UsbCdcAcmConnection(dev)
