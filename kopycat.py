#!/usr/bin/python

import argparse
from sys import stdin, exit
from getpass import getpass
from api.kopy import Kopy

class CLI(Kopy):

    urlFormat = "https://kopy.io/{documentId}#{passphrase}"
    # Should urlFormat support http:// too?

    description = \
"""\
Upload and read encrypted or plaintext files from kopy.io.

kopy.io is a pastebin with client-side encryption features. This allows you to
share sensitive information without fear of it being snooped on or spidered.
The cipher employed is AES-256-CBC.

kopycat and kopy.io are not suitable for secret information; proprietary
code snippets, yes. Nuclear launch codes, not so much. gpg is a safer bet
against determined adversaries.
"""

    examples = \
"""
Examples:

View a link from kopy.io:

    Warning: This exposes your AES passphrase to the anyone connected to the
    same system.

    kopycat http://kopy.io/75fEl#JpcOUW

View a link securely:

    kopycat http://kopy.io/75fEl -e # Prompts you for the passphrase
    kopycat http://kopy.io/75fEl -f /path/to/passphrase.txt

Upload a file to kopy.io:

    kopycat /path/to/file.txt
    kopycat /path/to/sensitive/file.txt -g 

Bugs? Feature requests? Contributions?
https://www.github.com/xmnr/kopycat
"""

    def _chopProtocol(self, url):

        if url.startswith("http://"): url=url[len("http://"):]
        elif url.startswith("https://"): url=url[len("https://"):]

        return url

    def kopyUrl(self, t):

        t = self._chopProtocol(t)
        return t.startswith("kopy.io")

    def parseUrl(self, url):

        url = self._chopProtocol(url)

        if not "/" in url: raise Exception("Bad URL.")

        chunk = url.split("/")[-1]
        if "#" in chunk:
            # FIXME support # in passphrases? urlencode them?
            documentId, passphrase = chunk.split("#")
            if not documentId: raise Exception("Bad URL; no document ID.")
            if not passphrase: passphrase = None
        else:
            documentId = chunk
            passphrase = None
            if not documentId: raise Exception("No document ID.")

        return documentId, passphrase

    def formatUrl(self, documentId, passphrase=None):

        return self.urlFormat.format(documentId=documentId,
                                    passphrase=passphrase or "")

    def upload(self, filename, passphrase, keep):

        try:
            document = open(filename, "r").read()
        except:
            print "Could not open file."
            exit(1)
        
        # TODO more error handling
        return self.createDocument(document, passphrase, keep)

    def download(self, documentId, passphrase):

        return self.retrieveDocument(documentId, passphrase)["data"]

    def outputDocument(self, document):

        print document
        exit(0)

    def outputUrl(self, documentId, passphrase=None):

        print self.formatUrl(documentId, passphrase)
        exit(0)

    def prompt(self):

        passphrase, confirm = True, False
        while passphrase != confirm:
            passphrase = getpass("Please enter your passphrase: ")
            confirm = getpass("Confirm passphrase: ")
            if passphrase != confirm:
                print "Confirmation failed."

        return passphrase

    def arguments(self):

        parser = argparse.ArgumentParser(description=self.description,
                                        epilog=self.examples,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("target", default=False, nargs="?",
                            help="File to upload or kopy.io URL to download."+ \
                            " If URL contains an anchor, it is taken to be the" + \
                            " passphrase; however, this method is insecure.")
        parser.add_argument("-u", "--sharable", default=False, action="store_true",
                            help="Embed passphrase into returned URL.")
        parser.add_argument("-d", "--download", help="Document ID to download.")
        parser.add_argument("-e", "--encryption", default=False, action="store_true",
                            help="Encrypt a document before uploading, or decrypt" + \
                            " a document after downloading.")
        parser.add_argument("-f", "--passphrase-file",
                            help="Read passphrase from a file.")
        parser.add_argument("-S", "--strip", default=False, action="store_true",
                            help="Strip whitespace from the file.")
        parser.add_argument("-s", "--stdin", default=False, action="store_true",
                            help="Read passphrase from stdin.")
        parser.add_argument("-g", "--generate-passphrase", default=False,
                            action="store_true", help="Generate a random " + \
                            "passphrase from the system's random device. " + \
                            "(Implies -u.)")
        parser.add_argument("-k", "--keep", type=int, default=600,
                            help="Number of seconds to store the document. " + \
                            "(Default is 600, or 10 minites.)") 

        return parser.parse_args(), parser.print_help

    def main(self):

        # FIXME doesn't try to validate arguments make sense, ie, doesn't check
        # if you're using --download and --encrypt together.
        # Also doesn't catch an errors.

        arguments, usage = self.arguments()

        # Fetching the passphrase

        passphrase = None

        if arguments.stdin:
            passphrase = stdin.read()
        elif arguments.passphrase_file:
            passphrase = open(arguments.passphrase_file).read()
        elif arguments.generate_passphrase:
            passphrase = self.generatePassword()
            arguments.sharable = True
        elif arguments.encryption:
            # Requires passphrase but none specified
            passphrase = self.prompt()

        if passphrase and arguments.strip:
            passphrase = passphrase.strip()

        # Executing the user's request
        if arguments.target:
            if self.kopyUrl(arguments.target):
                documentId, p = self.parseUrl(arguments.target)
                if p != None: passphrase = p # Should we print a warning?
                self.outputDocument(self.download(documentId, passphrase))
            else:
                self.outputUrl(self.upload(arguments.target, passphrase,
                                           arguments.keep),
                                           passphrase if arguments.sharable else None)
        elif arguments.download:
            self.outputDocument(self.download(arguments.download, passphrase))

        # Nothing to do
        else:

            usage()
            exit(1)

if __name__ == "__main__":
    CLI().main()
