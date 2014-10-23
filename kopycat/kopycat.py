"""
Library and utility to interact with kopy.io's API.
"""

import argparse
from base64 import b64encode, b64decode
from getpass import getpass
from hashlib import md5
from random import SystemRandom
from simplejson import loads
from requests import get, post 
from Crypto.Cipher import AES

class Kopy(object):

    """
    Implementation of the kopy.io API
    """

    url = "https://kopy.io/"
    apiEndpoint = "documents"
    verifyCert = False # kopy uses an invalid cert :'(

    keyLength = 256 / 8
    ivLength = 16
    blockSize = 16
    saltLength = 8
    passwordRandBytes = 100

    saltPadding = "Salted__" # this is half a block, and the salt is half a block
    ciphertextFormat = saltPadding + "{salt}{ciphertext}" # this is then b64'd

    def __init__(self):

        self.randomness = SystemRandom()

    def _randomBytes(self, length):

        if length <= 0: raise Exception("length must be a positive integer.")
        return "".join([chr(self.randomness.getrandbits(8)) for i in range(length)])

    def _generateSalt(self):

        return self._randomBytes(self.saltLength)

    def _parseCiphertext(self, ciphertext):

        output = b64decode(ciphertext)
        if not output.startswith(self.saltPadding):
            raise Exception("Bad salt padding.")
        if not len(output) % self.blockSize == 0:
            raise Exception("Message isn't sized correctly.")

        salt = output[len(self.saltPadding):self.blockSize]
        message = output[self.blockSize:]

        return salt, message

    def _formatCiphertext(self, salt, ciphertext):

        if len(salt) != self.saltLength:
            raise Exception("Bad salt.")
        if len(ciphertext) % self.blockSize != 0:
            raise Exception("Bad ciphertext.")

        return b64encode(self.ciphertextFormat.format(salt=salt,
                        ciphertext=ciphertext))

    def _aes(self, key, iv):

        return AES.new(key, AES.MODE_CBC, iv)

    def _getAESArgs(self, passphrase, salt):
        """
        Generate the key and IV from a passphrase using OpenSSL's derivation method.
        """

        if len(salt) != 8: raise Exception("Bad salt.")
        return self.opensslKeyDerivation(passphrase, salt,
                                        self.keyLength, self.ivLength)

    def _postDocument(self, document, encryption=False):

        pass

    def _getDocument(self, documentId):

        pass

    def _pad(self, message):
        """
        Add PKCS#7 padding; use byte value cooresponding to the number of
        characters to pad (ie, pad one byte with \x01). Pad to self.blockSize.
        """

        pad = self.blockSize - (len(message) % self.blockSize)
        return message + "".join([chr(pad) for i in range(pad)])

    def _unpad(self, message):
        """
        Remove PKCS#7 padding; use byte value cooresponding to the number of
        characters to pad (ie, pad one byte with \x01).
        """

        if len(message) % self.blockSize != 0:
            raise Exception("Message is not properly sized.")

        pad = ord(message[-1])
        if pad > self.blockSize: raise Exception("Bad padding.")

        output = message[:-pad]
        padding = message[-pad:]
        for i in padding:
            if ord(i) != pad: raise Exception("Bad padding.")

        return output

    def encrypt(self, document, passphrase, salt=None):
        """
        Encrypt a message with AES-256-CBC and OpenSSL-compatble passphrase.
        If no salt is given, a salt is generated; this is probably what you want.
        """

        if not salt: salt = self.generateSalt()
        key, iv = self._getAESArgs(passphrase, salt)
        document = self._pad(document)

        aes = self._aes(key, iv)
        return self._formatCiphertext(salt, aes.encrypt(document))

    def decrypt(self, document, passphrase):
        """
        Decrypt a message with AES-256-CBC and OpenSSL-compatible passphrase.
        """

        salt, ciphertext = self._parseCiphertext(document)
        key, iv = self._getAESArgs(passphrase, salt)
        aes = self._aes(key, iv)
        return self._unpad(aes.decrypt(ciphertext))

    def generatePassword(self, length=10):
        """
        Generate a random password of an arbitrary length, made up of hexadecimal
        digits.
        """

        if length <= 0: raise Exception("length must be a positive integer.")

        # FIXME: Would this method actually damage our randomness if
        # length > self.passwordRandBytes? I doubt it really adds anything for
        # length < self.passwordRandBytes.
        output = ""
        while len(output) < length:
            output += md5(self._randomBytes(self.passwordRandBytes)).hexdigest()
        return output[:length]

    def opensslKeyDerivation(self, password, salt, key_len, iv_len):
        """
        Derive the key and the IV from the given password and salt.
        Salt is the first 8 bytes of ciphertext.

        Stolen shamelessly from this Stack Overflow posting:
        https://stackoverflow.com/questions/13907841/implement-openssl-aes-encryption-in-python
        """
        dtot =  md5(password + salt).digest()
        d = [ dtot ]
        while len(dtot)<(iv_len+key_len):
            d.append( md5(d[-1] + password + salt).digest() )
            dtot += d[-1]
        return dtot[:key_len], dtot[key_len:key_len+iv_len]

    def createDocument(self, document):

        pass

    def retrieveDocument(self, documentId):

        pass

class CLI(Kopy):

    pass

#def main():
#    CLI().main()
