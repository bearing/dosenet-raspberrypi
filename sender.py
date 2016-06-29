# -*- coding: utf-8 -*-
"""
If you call sender.py from the command line, it will send 3 test packets.
See argparse for options.

Otherwise, this module is loaded to provide the ServerSender class.
"""

from __future__ import print_function

import socket
import argparse
import time
from contextlib import closing
import errno

from auxiliaries import set_verbosity, Config, PublicKey
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY

TCP_TIMEOUT = 5


class ServerSender(object):
    """
    Provides ServerSender.send_cpm() for sending UDP packets to the DoseNet
    server.
    """

    def __init__(self,
                 manager=None,
                 network_status=None,
                 address=DEFAULT_HOSTNAME,
                 port=None,
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

        self.address = address
        self.handle_input(
            manager, mode, port, network_status, config, publickey)

    def handle_input(
            self, manager, mode, port, network_status, config, publickey):

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
            # if mode is not a string or None, then mode.lower() raises this
            raise RuntimeError('Invalid ServerSender mode (choose TCP or UDP)')

        if self.mode == 'udp':
            if port is None:
                self.port = DEFAULT_UDP_PORT
            else:
                self.port = port
            self.vprint(3, 'ServerSender using UDP for {}:{}'.format(
                self.address, self.port))
        elif self.mode == 'tcp':
            if port is None:
                self.port = DEFAULT_TCP_PORT
            else:
                self.port = port
            self.vprint(3, 'ServerSender using TCP for {}:{}'.format(
                self.address, self.port))

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

    def construct_packet_new(self, timestamp, cpm, cpm_error, error_code=0):
        """
        New protocol version of construct packet.
        """

        c = ','
        try:
            raw_packet = (
                str(self.config.hash) + c +
                str(self.config.ID) + c +
                str(timestamp) + c +
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

    def send_data(self, encrypted):
        """
        Send data according to self.mode, and handle common errors
        """

        self.vprint(3, 'Trying to send data by {}'.format(self.mode))
        try:
            if self.mode == 'udp':
                self.send_udp(encrypted)
            elif self.mode == 'tcp':
                self.send_tcp(encrypted)
        except socket.gaierror as e:
            if e[0] == socket.EAI_AGAIN:
                # TCP and UDP
                # network is down, but NetworkStatus didn't notice yet
                # (resolving DNS like dosenet.dhcp.lbl.gov)
                self.vprint(
                    1, 'Failed to send packet! Address resolution error')
                self.network_up.update()
            else:
                self.vprint(1, 'Failed to send packet! Address error: ' +
                            '{}: {}'.format(*e))
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                # TCP
                # server is not accepting connections
                self.vprint(1, 'Failed to send packet! Connection refused')
            elif e[0] == errno.ENETUNREACH:
                # TCP and UDP
                # network is down, but NetworkStatus didn't notice yet
                # (IP like 131.243.51.241)
                self.vprint(
                    1, 'Failed to send packet! Network is unreachable')
                self.network_up.update()
            else:
                # consider handling errno.ECONNABORTED, errno.ECONNRESET
                self.vprint(1, 'Failed to send packet! Socket error: ' +
                            '{}: {}'.format(*e))
        except socket.timeout:
            # TCP
            self.vprint(1, 'Failed to send packet! Socket timeout')
            self.network_up.update()

    def send_udp(self, encrypted):
        """
        Send the encrypted packet over UDP
        """

        self.vprint(3, 'Sending encrypted UDP packet to {}:{}'.format(
            self.address, self.port))
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.sendto(encrypted, (self.address, self.port))
            self.vprint(
                3, 'UDP packet sent successfully (no client-side error)')

    def send_tcp(self, encrypted):
        """
        Send the encrypted packet over TCP
        """

        self.vprint(3, 'Sending encrypted TCP packet to {}:{}'.format(
            self.address, self.port))
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(TCP_TIMEOUT)   # generous timeout
            s.connect((self.address, self.port))
            s.sendall(encrypted)
            self.vprint(3, 'TCP packet sent successfully')

    def send_cpm(self, cpm, cpm_error, error_code=0):
        """Construct, encrypt, and send the packet"""

        packet = self.construct_packet(cpm, cpm_error, error_code=error_code)
        encrypted = self.encrypt_packet(packet)
        if self.network_up or self.network_up is None:
            self.send_data(encrypted)
        else:
            # TODO: feature add here
            self.vprint(2, 'Network DOWN, not sending packet')

    def send_cpm_new(self, timestamp, cpm, cpm_error, error_code=0):
        """
        New protocol for send_cpm
        """
        packet = self.construct_packet_new(
            timestamp, cpm, cpm_error, error_code=error_code)
        encrypted = self.encrypt_packet(packet)
        if self.network_up or self.network_up is None:
            self.send_data(encrypted)
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
        address=DEFAULT_HOSTNAME,
        port=None,
        n=3,
        encrypt=True):
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
        mode=mode, address=address, port=port,
        config=config_obj, publickey=key_obj, verbosity=3)

    try:
        station_id = config_obj.ID
    except AttributeError:
        station_id = '?'
    raw_packet = 'Test packet from station {} by mode {}'.format(
        station_id, mode)

    if encrypt:
        packet_to_send = sender.encrypt_packet(raw_packet)
    else:
        packet_to_send = raw_packet

    for _ in xrange(n):
        sender.send_data(packet_to_send)
        time.sleep(sleep_time)


if __name__ == '__main__':
    # send test packets
    parser = argparse.ArgumentParser(
        description='Sender for UDP/TCP data packets. ' +
        'Normally called from manager.py. ' +
        'Called directly, it will send 3 test packets to server. ' +
        'Specify udp or tcp on command line.')
    parser.add_argument(
        'mode', choices=['udp', 'tcp', 'UDP', 'TCP'], nargs='?', default='udp',
        help='The network protocol to use in sending test packets')
    parser.add_argument('-n', type=int, default=3, help='# packets')
    parser.add_argument('--config', '-c', type=str, default=DEFAULT_CONFIG,
                        help='config file location')
    parser.add_argument('--publickey', '-k', type=str,
                        default=DEFAULT_PUBLICKEY,
                        help='publickey file location')
    parser.add_argument('--hostname', '-a', type=str, default=DEFAULT_HOSTNAME,
                        help='hostname (web address or IP)')
    parser.add_argument('--port', '-p', type=int, default=None,
                        help='port')
    parser.add_argument('--no-encrypt', '-e', dest='encrypt',
                        action='store_false',
                        help='encrypt packet or don''t encrypt')
    args = parser.parse_args()

    send_test_packets(
        mode=args.mode.lower(), address=args.hostname, port=args.port,
        config=args.config, publickey=args.publickey, n=args.n,
        encrypt=args.encrypt)
