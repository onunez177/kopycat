"""
Library and utility to interact with kopy.io's API.
"""

from base64 import b64encode, b64decode
from hashlib import md5
from random import SystemRandom
from simplejson import loads, dumps
from requests import get, post 
from Crypto.Cipher import AES

class Kopy(object):

    """
    Implementation of the kopy.io API
    """

    url = "https://kopy.io/documents/"
    verifyCert = False # kopy uses an invalid cert :'(

    keyLength = 256 / 8
    ivLength = 16
    blockSize = 16
    saltLength = 8
    passwordRandBytes = 100

    saltPadding = "Salted__" # this is half a block, and the salt is half a block
    ciphertextFormat = saltPadding + "{salt}{ciphertext}" # this is then b64'd

    documentFormat = {"data":None, "security":None, "keep":None}.copy
    # note that documentFormat is a method
    # TODO put in some intelligent defaults, like a scheme, maybe a user-agent
    # to declare a paste was made with kopycat. Then again, maybe not.

    docNotFound = "Document not found."
    cryptoSchemes = ["default", "encrypted"]

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

    # FIXME the methods to interact with the API have 0 error handling.
    # The also don't have tests.

    def _composeDocument(self, document, encryption, keep):
        """
        Create a dictionary to represent the document, for requests.post()'s
        "data" parameter.
        """

        output = self.documentFormat()
        output["data"] = document
        output["keep"] = keep
        output["security"] = "encrypted" if encryption else "default"

        return output

    def _parseDocument(self, json):
        """
        Parse a JSON string into a native Python datastructure.
        """

        output = loads(json)
        return output

    def _postDocument(self, document, encryption=False, keep=600):
        """
        Send a request to the API to create a new document, and keep it for a
        certain number of seconds.

        Returns a dictionary with a "key" element, containing the new document's
        identifier.
        """

        return self._parseDocument(post(self.url, verify=self.verifyCert,
                                  data=self._composeDocument(document, encryption,
                                  keep)).content)

    def _getDocument(self, documentId):
        """
        Retrieve a document from the API.

        Returns a dictionary with the document's metadata.
        If the document was found, the "data" element will contain the actual
        document; the "security" element will tell you if its encrypted
        (a value of "default" means plaintext, otherwise its value will be
        "encrypted").
        If the document was not found, it will have a "message" element with the
        value "Document not found."
        """

        document = get(self.url + documentId, verify=self.verifyCert)
        if not document.status_code in [200, 404]: 
            raise Exception("Failed to retrieve document due to unkown error.")
        if not ("content-type" in document.headers and \
                document.headers["content-type"] == "application/json"):
            raise Exception("Document has invalid content-type.")
        else:
            return self._parseDocument(document.text)

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

        if not salt: salt = self._generateSalt()
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

    def createDocument(self, document, passphrase=None, keep=600):
        """
        Puts a document on kopy.io, and returns its identifier. If a passphrase
        is given, the document will be encrypted. The document will expire after
        "keep" seconds.
        """

        if passphrase != None: document = self.encrypt(document, passphrase)
        identifier = self._postDocument(document,
                                       encryption = (passphrase != None),
                                       keep=keep)
        if not "key" in identifier:
            raise Exception("An unknown error occured.")
        return identifier["key"]

    def retrieveDocument(self, documentId, passphrase=None):
        """
        Gets a document from kopy.io, decrypts it if its encrypted, and returns
        it as a dictionary. The actual document will be in the "data" element.
        """

        document = self._getDocument(documentId)

        # 404s
        if "message" in document and document["message"] == self.docNotFound:
            if "data" in document:
                raise Exception("kopy.io said document was not found; however," + \
                    " document contained value of '{}'.".format(document["data"]))
            else:
                raise Exception("Document was not found.")

        # Malformed documents
        if not "data" in document:
            raise Exception("Document contained no data.")

        # Handle encryption
        if "security" in document:
            if not document["security"] in self.cryptoSchemes:
                raise Exception("Document uses unknown encryption.")
            elif document["security"] == "encrypted":
                if passphrase == None:
                    raise Exception("Document is encrypted, but no passphrase" + \
                                    " was given.")
                else: # Encryption
                    document["data"] = self.decrypt(document["data"], passphrase)

            elif document["security"] == "default": # Plain text
                pass

        return document
