#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run on configured Raspberry Pi to test DoseNet server.

Have an Injector instance test-listening on TCP port 5101 (TESTING_TCP_PORT)
at dosenet.dhcp.lbl.gov

Authors:
    Brian Plimley
Affiliation:
    DoseNet
    Applied Nuclear Physics Division
    Lawrence Berkeley National Laboratory, Berkeley, U.S.A.
Last updated:
    2016-09-12
"""

from __future__ import print_function

import time

import auxiliaries as aux
from sender import ServerSender
from globalvalues import DEFAULT_CONFIG, DEFAULT_PUBLICKEY, TESTING_TCP_PORT


def main():
    config = aux.Config(DEFAULT_CONFIG)
    publickey = aux.PublicKey(DEFAULT_PUBLICKEY)

    sender = ServerSender(
        port=TESTING_TCP_PORT, config=config, publickey=publickey, mode='tcp')

    # test basic new data protocol
    test_new_data(sender)

    # test basic old data protocol
    test_old_data(sender)

    # test basic log
    test_log(sender)

    # test UnencryptedPacket
    test_unencrypted(sender)

    # test BadPacket
    test_bad_packet(sender)

    # test PacketLengthError
    test_packet_length(sender)

    # test HashLengthError
    test_hash_length(sender)

    # test ExcessiveCountrate
    test_countrate(sender)


def test_new_data(sender):
    """
    Test the new data protocol (including deviceTime) with a valid packet.
    """
    ts = time.time()
    cpm = 1.1
    cpm_error = 0.1
    sender.send_cpm_new(ts, cpm, cpm_error)


def test_old_data(sender):
    """
    Test the old data protocol (not including deviceTime) with a valid packet.
    """
    cpm = 1.1
    cpm_error = 0.1
    sender.send_cpm(cpm, cpm_error)


def test_log(sender):
    """
    Test the log injection with a valid log packet.
    """
    msg_code = 0
    msg_text = 'server test'
    sender.send_log(msg_code, msg_text)


def test_unencrypted(sender):
    """
    Test server's handling of an unencrypted packet.
    """
    message = 'Unencrypted text'
    sender.send_data(message)


def test_bad_packet(sender):
    """
    Test server's handling of a bad packet (mixed ASCII codes).
    """
    message = ''.join([chr(i) for i in range(11, 211, 5)])
    sender.send_data(message)


def test_hash_length(sender):
    """
    Test server's handling of a bad hash (not len 32).
    """

    # old data protocol
    message_full = sender.construct_packet(1.1, 0.1)
    message = message_full[2:]  # trim off first 2 characters of hash
    encrypted = sender.encrypt_packet(message)
    sender.send_data(encrypted)

    # new data protocol
    message_full = sender.construct_packet_new(time.time(), 1.1, 0.1)
    message = message_full[2:]  # trim off first 2 characters of hash
    encrypted = sender.encrypt_packet(message)
    sender.send_data(encrypted)

    # log protocol
    message_full = sender.construct_log_packet(0, 'hash test')
    message = message_full[2:]  # trim off first 2 characters of hash
    encrypted = sender.encrypt_packet(message)
    sender.send_data(encrypted)


def test_countrate(sender):
    """
    Test server's handling of an excessive countrate (>100).
    """

    # old data protocol
    sender.send_cpm(250, 0.1)
    # new data protocol
    sender.send_cpm_new(time.time(), 250, 0.1)


def test_packet_length(sender):
    """
    Test server's handling of a packet with wrong number of fields.
    """

    # too few fields (no error_code)
    too_few = ','.join([
        sender.config.hash, str(sender.config.ID), str(1.1), str(0.1)])
    encrypted = sender.encrypt_packet(too_few)
    sender.send_data(encrypted)

    # too many fields (add some numbers)
    too_many = ','.join(
        sender.config.hash, str(sender.config.ID), str(1.1), str(0.1),
        str(0), str(3.1416), str(2.71828))
    encrypted = sender.encrypt_packet(too_many)
    sender.send_data(encrypted)

if __name__ == '__main__':
    main()
