# -*- coding: utf-8 -*-
from __future__ import print_function

import cust_crypt
import socket


class ServerSender(object):
    """
    Sends UDP packets to the DoseNet server.
    """

    # TODO: include verbosity for test mode

    def __init__(self, manager):
        self.manager = manager
        # check that config and publickey exist and are valid
        self.encrypter = cust_crypt.PublicDEncrypt(
            key_file_lst=[self.manager.public_key])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # TODO: load these from somewhere
        self.address = 'dosenet.dhcp.lbl.gov'
        self.port = 5005

    def construct_packet(self, cpm, cpm_error, error_code=0):
        """basically copied from old code"""

        c = ','
        config = self.manager.config
        raw_packet = (
            str(config.hash) + c +
            str(config.ID) + c +
            str(cpm) + c +
            str(cpm_error) + c +
            str(error_code))
        encrypted_packet = self.encrypter.encrypt_message(raw_packet)[0]

        return encrypted_packet

    def send_packet(self, encrypted_packet):
        """basically copied from old code"""

        self.socket.sendto(encrypted_packet, (self.address, self.port))
        # TODO: try/except

    def send_cpm(self, cpm, cpm_error, error_code=0):
        """Wrapper for construct_packet and send_packet"""

        packet = self.construct_packet(cpm, cpm_error, error_code=error_code)
        self.send_packet(packet)
        # TODO: handle errors?
        # TODO: return status?
        return None
