from unittest import TestCase
from kopycat import CLI

class CLITest(TestCase):

    def setUp(self):
        self.c = CLI()

    # TODO type-checking and HTTP mocks (same goes for api/kopy.py)

    def testTime(self):

        self.assertEqual(self.c.parseTime("1m"), 60)
        self.assertEqual(self.c.parseTime("5m"), 5*60)
        self.assertEqual(self.c.parseTime("1h"), 3600)
        self.assertEqual(self.c.parseTime("100h"), 100*3600)
        self.assertEqual(self.c.parseTime("1d"), 86400)
        self.assertEqual(self.c.parseTime("365d"), 365*86400)

        self.assertRaises(Exception, self.c.parseTime, "10y")
        self.assertRaises(Exception, self.c.parseTime, "")
        self.assertRaises(Exception, self.c.parseTime, "m")
        self.assertRaises(Exception, self.c.parseTime, "1")
        self.assertRaises(Exception, self.c.parseTime, "1min")

    def testUrlParse(self):

        self.assertEqual(self.c.parseUrl("https://kopy.io/12345"), ("12345", None))
        self.assertEqual(self.c.parseUrl("https://kopy.io/12345#AAAAA"),
                        ("12345", "AAAAA"))
        self.assertEqual(self.c.parseUrl("http://kopy.io/12345"), ("12345", None))
        self.assertEqual(self.c.parseUrl("http://kopy.io/12345#AAAAA"),
                        ("12345", "AAAAA"))

        self.assertRaises(Exception, self.c.parseUrl, "https://kopy.io12345")
        self.assertRaises(Exception, self.c.parseUrl, "https://kopy.io/")
        self.assertRaises(Exception, self.c.parseUrl, "https://kopy.io#AAAAA")
        self.assertRaises(Exception, self.c.parseUrl, "http://kopy.io")
        self.assertRaises(Exception, self.c.parseUrl, "http://kopy.io#AAAAA")

    def testChop(self):

        self.assertEqual(self.c._chopProtocol("http://google.com"), "google.com")
        self.assertEqual(self.c._chopProtocol("https://google.com"), "google.com")
        self.assertEqual(self.c._chopProtocol("google.com"), "google.com")

    def testUrlFormat(self):

        self.assertEqual(self.c.formatUrl("12345"), "https://kopy.io/12345#")
        self.assertEqual(self.c.formatUrl("12345", "AAAAA"),
                        "https://kopy.io/12345#AAAAA")

    def testKopyUrl(self):

        self.assertTrue(self.c.kopyUrl("https://kopy.io/12345"))
        self.assertTrue(self.c.kopyUrl("https://kopy.io/12345#AAAAA"))
        self.assertTrue(self.c.kopyUrl("http://kopy.io/12345"))
        self.assertTrue(self.c.kopyUrl("http://kopy.io/12345#AAAAA"))
        
        # Should kopyUrl raise errors for URLs w/o a document ID?
