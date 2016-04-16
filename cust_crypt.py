# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA as rsa


class PublicDEncrypt:

    def __init__(self, key_file_lst=[]):

        self.private_key = None
        self.public_key = None

        for key_file in key_file_lst:
            key = self.read_key_file(key_file)
            if not key:
                continue
            if key.has_private():
                self.private_key = key
            elif key.can_encrypt():
                self.public_key = key

    def encrypt_message(self, message):
        if self.public_key is None:
            return None
        else:
            return self.public_key.encrypt(message, 32)

    def read_key_file(self, key_file):
        with open(key_file, 'r') as f:
            return rsa.importKey(f.read())

    def decrypt_message(self, message):
        if self.private_key is None:
            return None
        else:
            return self.private_key.decrypt(message)
