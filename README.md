kopycat - kopy.io library and CLI
=================================

kopy.io is a paste service with support for AES-256-CBC encryption.

The encryption happens client-side, in the browser, with Crypto-JS. This means
that kopy.io cannot see the content of your documents.

This library implements kopy.io's API.

## Roadmap

* Write the CLI
 * As the name implies, it is meant to behave like cat; you cat kopycat a kopy.io
   paste to stdin, or a file to kopy.io
 * It will be just as friendly to pipelining, so you can, say, grep certain
   entries out of a log, and put the on kopy.io to share over IRC etc.
* Its been reccomended that I avoid using the PyCrypto library; more research
  is needed.
