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
import numpy as np
from contextlib import closing
from Crypto.Cipher import AES

from auxiliaries import set_verbosity, Config, PublicKey
from globalvalues import DEFAULT_HOSTNAME, DEFAULT_SENDER_MODE
from globalvalues import DEFAULT_UDP_PORT, DEFAULT_TCP_PORT
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY, DEFAULT_AESKEY

TCP_TIMEOUT = 5
D3S_PREPEND_STR = '{:05d}'


class ServerSender(object):
    """
    Provides ServerSender.send_cpm() for sending UDP packets to the DoseNet
    server.
    """

    def __init__(self,
                 manager=None,
                 address=DEFAULT_HOSTNAME,
                 port=None,
                 config=None,
                 publickey=None,
                 aes=None,
                 verbosity=1,
                 logfile=None,
                 mode=None,
                 ):
        """
        network_status, config, publickey, aes loaded from manager
          if not provided.
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
            manager, mode, port, config, publickey, aes)

    def handle_input(
            self, manager, mode, port, config, publickey, aes):

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

        if aes is None:
            if manager is None:
                self.vprint(2, 'ServerSender starting without AES key')
                self.aes = None
            elif manager.aes is None:
                self.vprint(2, 'ServerSender starting without AES key')
                self.aes = None
            else:
                self.aes = manager.aes
        else:
            self.aes = aes

    def construct_packet(self, cpm, cpm_error, error_code=0):
        """
        Construct the raw packet string. (basically copied from old code)

        hash,ID,cpm,cpm_error,error_code
        """

        try:
            raw_packet = ','.join(
                [str(self.config.hash),
                 str(self.config.ID),
                 str(cpm),
                 str(cpm_error),
                 str(error_code)]
            )
        except AttributeError:      # on self.config.hash
            raise MissingFile('Missing or broken Config object')
        else:
            self.vprint(3, 'Constructed packet')
            return raw_packet

    def construct_packet_new(self, timestamp, cpm, cpm_error, error_code=0):
        """
        New protocol version of construct packet.

        hash,ID,timestamp,cpm,cpm_error,error_code
        """

        try:
            raw_packet = ','.join(
                [str(self.config.hash),
                 str(self.config.ID),
                 str(timestamp),
                 str(cpm),
                 str(cpm_error),
                 str(error_code)]
            )
        except AttributeError:      # on self.config.hash
            raise MissingFile('Missing or broken Config object')
        else:
            self.vprint(3, 'Constructed packet')
            return raw_packet

    def construct_packet_new_D3S(self, timestamp, spectra, error_code=0):
        """
        TCP version of construct packet.
        """

        # convert spectra to a string representation that won't interfere with
        #   injector's parsing (no commas)
        spectra_str = str(spectra).replace(',', ';')
        try:
            raw_packet = ','.join(
                [str(self.config.hash),
                 str(self.config.ID),
                 str(timestamp),
                 spectra_str,
                 str(error_code)]
            )
        except AttributeError:      # on self.config.hash
            raise MissingFile('Missing or broken Config object')
        else:
            self.vprint(3, 'Constructed packet')
            return raw_packet

    def construct_log_packet(self, msg_code, msg_text):
        """
        Send a message to be recorded in the server log database.

        hash,ID,"LOG",msg_code,msg_text
        """

        if not isinstance(msg_code, int):
            raise TypeError('msg_code should be an int')
        try:
            raw_packet = ','.join(
                [str(self.config.hash),
                 str(self.config.ID),
                 'LOG',
                 str(msg_code),
                 str(msg_text)]
            )
        except AttributeError:      # on self.config.hash
            raise MissingFile('Missing or broken Config object')
        else:
            self.vprint(3, 'Constructed log packet')
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

    def encrypt_packet_aes(self, raw_packet):
        """Encrypt with AES (for D3S). Prepend message length."""

        self.vprint(3, 'AES encrypting packet: {}'.format(raw_packet))
        try:
            block_size = 16
            pad_length = block_size - (len(raw_packet) % block_size)
            if pad_length == block_size:
                encrypted = self.aes.encrypt(raw_packet)
            else:
                pad = ' ' * pad_length
                encrypted = self.aes.encrypt(raw_packet + pad)
        except AttributeError:
            raise MissingFile('Missing or broken AES object')
        else:
            prepend = D3S_PREPEND_STR.format(len(encrypted))
            # prepend does NOT include its own string in the message length
            full_packet = prepend + encrypted
            return full_packet

    def send_data(self, encrypted):
        """
        Send data according to self.mode
        """

        self.vprint(3, 'Trying to send data by {}'.format(self.mode))
        if self.mode == 'udp':
            self.send_udp(encrypted)
        elif self.mode == 'tcp':
            self.send_tcp(encrypted)

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
            received = s.recv(1024)
            self.vprint(3, 'TCP received {}'.format(received))
            branch, flag = self.handle_return_packet(received)
            if branch is not None:
                self.vprint(3, 'Branch: {}'.format(branch))
                self.vprint(3, 'Update flag: {}'.format(flag))
                if self.manager:
                    self.manager.branch = branch
                    self.manager.quit_after_interval = flag
                else:
                    self.vprint(
                        1, 'No manager, not saving branch and updateflag')
            else:
                self.vprint(2, 'Bad or missing return packet!')
            self.vprint(3, 'TCP packet sent successfully')

    def send_cpm(self, cpm, cpm_error, error_code=0):
        """Construct, encrypt, and send the packet"""

        packet = self.construct_packet(cpm, cpm_error, error_code=error_code)
        encrypted = self.encrypt_packet(packet)
        self.send_data(encrypted)

    def send_cpm_new(self, timestamp, cpm, cpm_error, error_code=0):
        """
        New protocol for send_cpm
        """
        packet = self.construct_packet_new(
            timestamp, cpm, cpm_error, error_code=error_code)
        encrypted = self.encrypt_packet(packet)
        self.send_data(encrypted)

    def send_log(self, msg_code, msg_text):
        """
        Send a log message
        """
        packet = self.construct_log_packet(msg_code, msg_text)
        encrypted = self.encrypt_packet(packet)
        self.send_data(encrypted)

    def send_spectra_new_D3S(self, timestamp, spectra, error_code=0):
        """
        TCP for sending spectra
        """
        packet = self.construct_packet_new_D3S(
            timestamp, spectra, error_code=error_code)
        encrypted = self.encrypt_packet_aes(packet)
        self.send_data(encrypted)

    def handle_return_packet(self, received):
        """
        Extracts the git tag from sender and puts it into a list.
        """
        try:
            received = [x.strip() for x in received.split(',')]
            branch = received[0]
            if int(received[1]) == 0:
                flag = False
            else:
                flag = True
            assert len(received) == 2
        except (AttributeError, IndexError, ValueError, AssertionError):
            return None, None
        else:
            return branch, flag

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
        encrypt=True,
        raw_packet=None):
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
    if raw_packet is None:
        raw_packet = 'Test packet from station {} by mode {}'.format(
            station_id, mode)

    if encrypt:
        packet_to_send = sender.encrypt_packet(raw_packet)
    else:
        packet_to_send = raw_packet

    for _ in xrange(n):
        sender.send_data(packet_to_send)
        time.sleep(sleep_time)


def send_log_message(
        mode=DEFAULT_SENDER_MODE,
        config=DEFAULT_CONFIG,
        publickey=DEFAULT_PUBLICKEY,
        address=DEFAULT_HOSTNAME,
        port=None,
        msgcode=0,
        message='ServerSender test'):
    """
    Send a log message to the server.
    """

    try:
        config_obj = Config(config)
    except IOError:
        # file doesn't exist
        config_obj = None

    try:
        key_obj = PublicKey(publickey)
    except IOError:
        # file doesn't exist
        key_obj = None

    sender = ServerSender(
        mode=mode, address=address, port=port,
        config=config_obj, publickey=key_obj, verbosity=3)

    if key_obj is None:
        # no encryption
        if config is None:
            # no ID
            packet = ','.join(msgcode, message)
            sender.send_data(packet)
        else:
            # has ID
            packet = ','.join(
                sender.config.hash, sender.config.ID, msgcode, message)
            sender.send_data(packet)
    else:
        # encryption
        if config is None:
            # no ID
            packet = ','.join(msgcode, message)
            encrypted = sender.encrypt_packet(packet)
            sender.send_data(encrypted)
        else:
            # standard, full functionality
            sender.send_log(msgcode, message)


def send_test_d3s_packet(
        config=DEFAULT_CONFIG,
        publickey=DEFAULT_PUBLICKEY,
        aeskey=DEFAULT_AESKEY,
        port=None,
        encrypt=True):
    """
    Send a test packet in the format of the D3S data.
    """

    try:
        config_obj = Config(config)
    except IOError:
        config_obj = None
    try:
        key_obj = PublicKey(publickey)
    except IOError:
        key_obj = None
        if encrypt:
            print("no publickey, can't encrypt")
        encrypt = False
    try:
        with open(aeskey, 'r') as aesfile:
            aeskey = aesfile.read()
            aes = AES.new(aeskey, mode=AES.MODE_ECB)
    except IOError:
        aes = None
        if encrypt:
            print("no AES key, can't encrypt")
        encrypt = False

    sender = ServerSender(
        port=port, config=config_obj, publickey=key_obj, aes=aes, verbosity=3)

    spectrum = [int(np.random.random() * 3) for _ in xrange(4096)]
    raw_packet = sender.construct_packet_new_D3S(time.time(), spectrum)

    if encrypt:
        packet_to_send = sender.encrypt_packet_aes(raw_packet)
    else:
        packet_to_send = raw_packet

    try:
        sender.send_data(packet_to_send)
    except socket.timeout:
        print('timeout!')

    return packet_to_send


if __name__ == '__main__':
    # send a test log entry
    parser = argparse.ArgumentParser(
        description='Sender for UDP/TCP data packets. ' +
        'Normally called from manager.py. ' +
        'Called directly, it will send a log message to the server.')
    parser.add_argument('--mode', '-n', choices=['udp', 'tcp', 'UDP', 'TCP'],
                        default=DEFAULT_SENDER_MODE,
                        help='Network protocol to use')
    parser.add_argument('--config', '-g', type=str, default=DEFAULT_CONFIG,
                        help='config file location')
    parser.add_argument('--publickey', '-k', type=str,
                        default=DEFAULT_PUBLICKEY,
                        help='publickey file location')
    parser.add_argument('--hostname', '-a', type=str, default=DEFAULT_HOSTNAME,
                        help='hostname (web address or IP)')
    parser.add_argument('--port', '-p', type=int, default=None,
                        help='port')
    parser.add_argument('--msgcode', '-c', type=int, default=0,
                        help='message code for log')
    parser.add_argument('--message', '-m', type=str,
                        default='ServerSender test',
                        help='message text for log')
    args = parser.parse_args()

    send_log_message(
        mode=args.mode, address=args.hostname, port=args.port,
        config=args.config, publickey=args.publickey,
        msgcode=args.msgcode, message=args.message)
