# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA as rsa


class PublicDEncrypt:

    def __init__(self, key_file_lst=[]):

        for key_file in key_file_lst:
            key = self.read_key_file(key_file)
            if not key:
                continue
            if key.has_private():
                self.private_key = key
            elif key.can_encrypt():
                self.public_key = key

    def encrypt_message(self, message):
        return self.public_key.encrypt(message, 32)

    def read_key_file(self, key_file):
        try:
            f = open(key_file, 'r')
        except:
            print '\t\t\t ERROR'
            print '\t\t ~~~~ Could not find key file - where is it? ~~~~'
            return None
        return rsa.importKey(f.read())

    def decrypt_message(self, message):
        return self.private_key.decrypt(message)
