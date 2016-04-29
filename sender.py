# -*- coding: utf-8 -*-
from __future__ import print_function

import socket

from auxiliaries import set_verbosity
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_PORT


class ServerSender(object):
    """
    Provides ServerSender.send_cpm() for sending UDP packets to the DoseNet
    server.
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
        if manager:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self)

        self.handle_input(manager, network_status, config, publickey)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.address = address
        self.port = port

    def handle_input(self, manager, network_status, config, publickey):

        # TODO: this stuff is messy. Is there a cleaner way using exceptions?
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

    def construct_packet(self, cpm, cpm_error, error_code=0):
        """
        Construct the raw packet string. (basically copied from old code)
        """

        c = ','
        try:
            raw_packet = (
                str(self.config.hash) + c +
                str(self.config.ID) + c +
                str(cpm) + c +
                str(cpm_error) + c +
                str(error_code))
        except AttributeError:      # on self.config.hash
            raise MissingFile('Missing or broken Config object')
        else:
            return raw_packet

    def encrypt_packet(self, raw_packet):
        """Encrypt the raw packet"""

        try:
            encrypted = self.encrypter.encrypt_message(raw_packet)[0]
        except AttributeError:
            raise MissingFile('Missing or broken PublicKey object')
        else:
            return encrypted

    def send_packet(self, encrypted):
        """
        Send the encrypted packet. (basically copied from old code)
        """

        self.socket.sendto(encrypted, (self.address, self.port))

    def send_cpm(self, cpm, cpm_error, error_code=0):
        """Construct, encrypt, and send the packet"""

        packet = self.construct_packet(cpm, cpm_error, error_code=error_code)
        encrypted = self.encrypt_packet(packet)
        if self.network_up or self.network_up is None:
            self.send_packet(encrypted)
            # except socket.error as e:
            #     self.vprint(1, '~ Socket error! {}'.format(e))
            #     # force update of network status - could be just no network
            #     self.network_up.update()
        else:
            # TODO: feature add here
            self.vprint(2, 'Network DOWN, not sending packet')


class PacketError(Exception):
    pass


class MissingFile(PacketError):
    pass
