# -*- coding: utf-8 -*-
from __future__ import print_function

import socket
import argparse
import time

from auxiliaries import set_verbosity, Config, PublicKey
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_PORT, DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY


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
                 logfile=None,
                 mode=None,
                 ):
        """
        network_status, config, publickey loaded from manager if not provided.
        address and port take system defaults, although without config and
          publickey, address and port will not be used.
        """

        self.v = verbosity
        if manager and logfile is None:
            set_verbosity(self, logfile=manager.logfile)
        else:
            set_verbosity(self, logfile=logfile)

        self.handle_input(manager, mode, network_status, config, publickey)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.address = address
        self.port = port

    def handle_input(self, manager, mode, network_status, config, publickey):

        # TODO: this stuff is messy. Is there a cleaner way using exceptions?
        if manager is None:
            self.vprint(1, 'ServerSender starting without Manager object')
        self.manager = manager

        try:
            if mode is None:
                self.mode = DEFAULT_SENDER_MODE
            elif mode.lower() == 'udp':
                self.mode = 'udp'
            elif mode.lower() == 'tcp':
                self.mode = 'tcp'
            else:
                raise RuntimeError(
                    'Invalid ServerSender mode (choose TCP or UDP)')
        except AttributeError:
            raise RuntimeError('Invalid ServerSender mode (choose TCP or UDP)')

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
            self.vprint(3, 'Constructed packet')
            return raw_packet

    def encrypt_packet(self, raw_packet):
        """Encrypt the raw packet"""

        self.vprint(3, 'Encrypting packet: {}'.format(raw_packet))
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

        self.vprint(3, 'Sending encrypted packet')
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


def send_test_packets(
        mode=DEFAULT_SENDER_MODE,
        config=DEFAULT_CONFIG,
        publickey=DEFAULT_PUBLICKEY,
        n=3):
    """
    Send n (default 3) test packets to the DoseNet server.
    """

    sleep_time = 2      # seconds

    try:
        config_obj = Config(config)
    except IOError:
        # file doesn't exist
        config_obj = None
    key_obj = PublicKey(publickey)

    sender = ServerSender(
        mode=mode, config=config_obj, publickey=key_obj, verbosity=3)

    try:
        station_id = config_obj.ID
    except AttributeError:
        station_id = '?'
    raw_packet = 'Test packet from station {} by mode {}'.format(
        station_id, mode)

    encrypted = sender.encrypt_packet(raw_packet)

    for _ in xrange(n):
        sender.send_packet(encrypted)
        time.sleep(sleep_time)


if __name__ == '__main__':
    # send test packets
    parser = argparse.ArgumentParser(
        description='Sender for UDP/TCP data packets. ' +
        'Normally called from manager.py. ' +
        'Called directly, it will send 3 test packets to server. ' +
        'Specify udp or tcp on command line.')
    parser.add_argument(
        'mode', choices=['udp', 'tcp'], nargs='?', default='udp',
        help='The network protocol to use in sending test packets')
    args = parser.parse_args()

    send_test_packets(
        mode=args.mode, config=DEFAULT_CONFIG, publickey=DEFAULT_PUBLICKEY)
