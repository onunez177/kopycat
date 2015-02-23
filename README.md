`kopycat` - command-line access to kopy.io
==========================================

[kopy.io](http://kopy.io) is a pasting site with support for client-side
encryption, using [Crypto-JS](https://code.google.com/p/crypto-js/).

`kopycat` is a command-line utility to interact with kopy.io. It is friendly to
pipelining and shell scripting, and supports the same form of encryption as the
web site. As the name implies, its meant to work just like `cat`.

--------------------------------------------------------------------------------

## Encryption

Documents are encrypted with AES-256-CBC using a passphrase; the key and IV are
derived from the passphrase in a method compatible with
[OpenSSL](https://www.openssl.org/docs/crypto/EVP_BytesToKey.html).

URLs from kopy.io generally have the passphrase embedded in the anchor attribute.
Alternatively, if the anchor attribute is left blank, the user will be prompted
for a passphrase.

    https://kopy.io/<document>#<passphrase>

## Security

This software have not been audited by cryptographers. This utility
is not intended to protect truly secret information. It is meant to safegaurd
sensitive information.

Whats the distinction? Sensitive information is to be shared, but with a limited
audience; its not meant to be public, but if prying eyes found it the costs would
be minimal. Secret information is the kind of valuable data an adversary might
go to great lengths to steal. You probably want `gpg` for that.

Additionally, if you use the option which allows you to specify your passphrase
on the command line, you are leaking the passphrase to any other user on the same
system as well as recording it in your bash history.

## Installation

You'll need to install the Python development package, which is a dependency of
PyCrypto. On Debian systems, you the package name is `python-dev`.

`apt-get install python-dev`

After that, download the .zip from GitHup, unzip it into your desired directory,
and install the dependencies.

`pip install -r requirements.txt`

Now you're ready to go.

## Examples

* Download a document from kopy.io

`kopycat http://kopy.io/75fEl#JpcOUW > file.txt` 

* Prompt for a password, rather than exposing it in /proc/pid/cmdline

`kopycat http://kopy.io/75fEl -e > file.txt`

* Upload an encrypted copy of 500 errors from your Apache logs, removing IP
addresses to preserve your user's anonymity.

`grep 500 /var/log/apache2/access.log | cut -d" " -f2-13 | kopycat -g`

## API

The Python library implementing the API (`api/kopy.py`) is available for
integrating kopy.io into your own projects.

## Contributions

All contributions are welcome! If you add a pull request, I'll review and merge
it as soon as I can.

Have a look at ROADMAP.md.

## Known Issues

kopy.io uses a TLS certificate for a different domain, so verification fails.
Right now, `kopycat` simply doesn't perform verification -- opening the door
to MitM attacks.

This will eventually be fixed in `kopycat` (by assuming the certificate is static,
which is not a fantastic solution), but I have no control of whether this is fixed
on the server side.

'#' characters in passwords do not work; newlines and linefeeds can also cauce problems.

## Bugs and feature requests

Thanks for spotting it !

Please add an issue to the
[GitHub repository](https://www.github.com/xmnr/kopycat).
