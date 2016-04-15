# -*- coding: utf-8 -*-
from __future__ import print_function

import socket
import warnings

from auxiliaries import set_verbosity
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_PORT


class ServerSender(object):
    """
    Sends UDP packets to the DoseNet server.
    """

    def __init__(self,
                 manager=None,
                 network_status=None,
                 address=DEFAULT_HOSTNAME,
                 port=DEFAULT_PORT,
                 config=None,
                 publickey=None,
                 verbosity=1,
                 ):
        """
        network_status, config, publickey loaded from manager if not provided.
        address and port take system defaults, although without config and
          publickey, address and port will not be used.
        """

        self.v = verbosity
        set_verbosity(self)

        if manager is None:
            self.vprint(1, 'ServerSender starting without Manager object')
        self.manager = manager

        if network_status is None:
            if manager is None:
                self.vprint(
                    1, 'ServerSender starting without network status object')
                self.network_up = None
            else:
                self.network_up = manager.network_up
        else:
            self.network_up = network_status

        if config is None:
            if manager is None:
                self.vprint(1, 'ServerSender starting without config file')
                self.config = None
            else:
                self.config = manager.config
        else:
            self.config = config

        if publickey is None:
            if manager is None:
                self.vprint(1, 'ServerSender starting without publickey file')
                self.encrypter = None
            elif manager.publickey is None:
                self.vprint(1, 'ServerSender starting without publickey file')
                self.encrypter = None
            else:
                self.encrypter = manager.publickey.encrypter
        else:
            self.encrypter = publickey.encrypter

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.address = address
        self.port = port

    def construct_packet(self, cpm, cpm_error, error_code=0):
        """basically copied from old code"""

        if self.config is not None:
            c = ','
            raw_packet = (
                str(self.config.hash) + c +
                str(self.config.ID) + c +
                str(cpm) + c +
                str(cpm_error) + c +
                str(error_code))
            if self.encrypter is not None:
                encrypted_packet = (
                    self.encrypter.encrypt_message(raw_packet)[0])
                # encrypt_message() returns a length-1 tuple, hence the [0]
                return encrypted_packet
            else:
                self.vprint(1, 'No publickey; cannot encrypt packet')
                if self.v >= 4:
                    warnings.warn(
                        'No publickey; cannot encrypt packet', PacketWarning)
                return None
        else:
            self.vprint(1, 'No config file; cannot construct packet')
            if self.v >= 4:
                warnings.warn(
                    'No config file; cannot construct packet', PacketWarning)
            return None

    def send_packet(self, encrypted_packet):
        """basically copied from old code"""

        if self.network_up or self.network_up is None:
            try:
                self.socket.sendto(encrypted_packet, (self.address, self.port))
            except socket.error as e:
                self.vprint(1, '~ Socket error! {}'.format(e))
                # force update of network status - could be just no network
                self.network_up.update()
        else:
            self.vprint(2, 'Network DOWN, not sending packet')

    def send_cpm(self, cpm, cpm_error, error_code=0):
        """Wrapper for construct_packet and send_packet"""

        packet = self.construct_packet(cpm, cpm_error, error_code=error_code)
        if packet is None:
            self.vprint(2, 'Packet not sent')
            return None
        else:
            self.send_packet(packet)
            return None
        # TODO: handle errors?
        # TODO: return status?


class PacketWarning(UserWarning):
    pass
