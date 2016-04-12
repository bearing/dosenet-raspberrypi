# -*- coding: utf-8 -*-
from __future__ import print_function

import socket

DEFAULT_HOSTNAME = 'dosenet.dhcp.lbl.gov'
DEFAULT_PORT = 5005


class ServerSender(object):
    """
    Sends UDP packets to the DoseNet server.
    """

    # TODO: include verbosity for test mode

    def __init__(self,
                 manager=None,
                 network_status=None,
                 address=DEFAULT_HOSTNAME,
                 port=DEFAULT_PORT,
                 config=None,
                 publickey=None,
                 ):
        """
        network_status, config, publickey loaded from manager if not provided.
        address and port take system defaults, although without config and
          publickey, address and port will not be used.
        """

        if manager is None:
            print('ServerSender starting without Manager object')
        self.manager = manager

        if network_status is None:
            if manager is None:
                print('ServerSender starting without network status object')
            else:
                self.network_up = manager.network_up
        else:
            self.network_up = network_status

        if config is None:
            if manager is None:
                print('ServerSender starting without config file')
                self.config = None
            else:
                self.config = manager.config
        else:
            self.config = config

        if publickey is None:
            if manager is None:
                print('ServerSender starting without publickey file')
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
                return encrypted_packet
            else:
                print('No publickey; cannot encrypt packet')
                return None
        else:
            print('No config file; cannot construct packet')
            return None

    def send_packet(self, encrypted_packet):
        """basically copied from old code"""

        try:
            self.socket.sendto(encrypted_packet, (self.address, self.port))
        except socket.error as e:
            print('~ Socket error! {}'.format(e))

    def send_cpm(self, cpm, cpm_error, error_code=0):
        """Wrapper for construct_packet and send_packet"""

        packet = self.construct_packet(cpm, cpm_error, error_code=error_code)
        if packet is None:
            print('Packet not sent')
            return None
        else:
            self.send_packet(packet)
            return None
        # TODO: handle errors?
        # TODO: return status?
