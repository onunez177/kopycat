from unittest import TestCase, main 
from api.kopy import Kopy
from base64 import b64encode, b64decode

class KopyTest(TestCase):

    # TODO theres no checks for inputs of the wrong type.

    plaintext = "attack at dawn"
    ciphertext = "U2FsdGVkX1/XnDGaEACaoTEhm7YsBicuJNgLrFSMKe0="
    passphrase = "9ACJQzDPFiVJXC"
    salt = '\xd7\x9c1\x9a\x10\x00\x9a\xa1' 

    k = Kopy()
    s = "Salted__"

    def testPadding(self):

        self.assertEqual(self.k._pad("A"*16), "A"*16+"\x10"*16)
        self.assertEqual(self.k._pad("A"*15), "A"*15+"\x01")
        self.assertEqual(self.k._pad("A"*31), "A"*31+"\x01")
        self.assertEqual(self.k._pad("A"*8), "A"*8+"\x08"*8)
        self.assertEqual(self.k._pad("A"*24), "A"*24+"\x08"*8)
        self.assertEqual(self.k._pad(""), "\x10"*16)

    def testUnpadding(self):

        self.assertEqual(self.k._unpad("A"*15+"\x01"), "A"*15)
        self.assertEqual(self.k._unpad("A"*24+"\x08"*8), "A"*24)
        self.assertEqual(self.k._unpad("\x10"*16), "")
        self.assertEqual(self.k._unpad("A"*16+"\x10"*16), "A"*16)

        self.assertRaises(Exception, self.k._unpad, "A"*14+"\x01\x02")
        self.assertRaises(Exception, self.k._unpad, "A"*15)
        self.assertRaises(Exception, self.k._unpad, "A"*15+"\x02")
        self.assertRaises(Exception, self.k._unpad, "A"*256+"\xff"*256)

    # TODO more testing for crypto.
    # - Tests for incorrectly sized inputs

    def testEncryption(self):

        self.assertEqual(self.k.encrypt(self.plaintext, self.passphrase, salt=self.salt),
                        self.ciphertext)

    def testDecryption(self):

        self.assertEqual(self.k.decrypt(self.ciphertext, self.passphrase),
                        self.plaintext)

    # It would be nice if these tests weren't just lumps of binary
    # Doesn't seem to be a good alternative though

    def testKeyDerivation(self):

        self.assertEqual(self.k.opensslKeyDerivation("AAAAAAAAAA",
                         "AAAAAAAA", 32, 16),
                         ('\x9f\xe1%\xb6h\x0bC\xa6)S\xd4\xccoN\x08\xbfK\xa5' + \
                         '\xf8k\xeeH\xd2b\x0bZ\xb6\xc6\x80\xa0^K',
                         '\xb1\x9frVm)\x0b\xa7\x04"@\xcc\x87\x7f\x91\x10'))
    def testAESArgs(self):

        self.assertEqual(self.k._getAESArgs("password", "A"*8),
                        ('\xd5\x90\x8c\xbb\xcbvB\xd6\xe3;\xc2\xffeP!\xa5\x8a' + \
                        '\xb6aT\xe3\x19\x1a\xe3|\xe1|\x00=\xc8]7',
                        '\xda\xc2B\xd0T\xf3\xcb\xd6\x97X\xa6\\v#\xf4\xd5'))

        self.assertRaises(Exception, self.k._getAESArgs, "A"*10, "B"*7)
        self.assertRaises(Exception, self.k._getAESArgs, "A"*10, "B"*9)

    def testCryptoFormat(self):

        self.assertEqual(self.k._formatCiphertext("A"*8, "B"*16),
                        b64encode(self.s + "A"*8 + "B"*16))
        self.assertEqual(self.k._formatCiphertext("A"*8, "B"*32),
                        b64encode(self.s + "A"*8 + "B"*32))

        self.assertRaises(Exception, self.k._formatCiphertext, "A"*7, "B"*16)
        self.assertRaises(Exception, self.k._formatCiphertext, "A"*8, "B"*15)

    def testCryptoParse(self):

        self.assertEqual(self.k._parseCiphertext(
                        b64encode(self.s + "A"*8 + "B"*16)),
                        ("A"*8, "B"*16))
        self.assertEqual(self.k._parseCiphertext(
                        b64encode(self.s + "A"*8 + "B"*32)),
                        ("A"*8, "B"*32))
        
        self.assertRaises(Exception, self.k._parseCiphertext,
                          b64encode("A"*8 + "B"*16))
        self.assertRaises(Exception, self.k._parseCiphertext,
                          "Salted_" + "A"*8 + "B"*16)
        # Bad salt padding ("Salted__")

        self.assertRaises(Exception, self.k._parseCiphertext, 
                         b64encode(self.s + "A"*7 + "B"*16))
        # Bad salt

        self.assertRaises(Exception, self.k._parseCiphertext,
            b64encode(self.s + "A"*8 + "B"*15))
        self.assertRaises(Exception, self.k._parseCiphertext,
            b64encode(self.s + "A"*8 + "B"*33))
        # Bad padding

    def testRandom(self):

        self.assertEqual(len(self.k._randomBytes(100)), 100)

        self.assertRaises(Exception, self.k._randomBytes, 0)
        self.assertRaises(Exception, self.k._randomBytes, -1)

    def testPassword(self):

        self.assertEqual(len(self.k.generatePassword(100)), 100)

        # FIXME no way to differentiate this raising an exception and 
        # _randomBytes, atm
        self.assertRaises(Exception, self.k.generatePassword, 0)
        self.assertRaises(Exception, self.k.generatePassword, -1)

    def testSalt(self):

        self.assertEqual(len(self.k._generateSalt()), 8)

    # TODO set up mocks to test HTTP components

class CLITest(TestCase):

    pass

if __name__ == "__main__": main()
