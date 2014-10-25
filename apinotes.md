Notes on kopy.io
================

kopy.io is a PasteBin-like site, which supports client-side encryption through
the Crypto-JS library.

kopy.io doesn't yet have official documentation; this is understandable, it was
launched yesterday. These notes are gleaned from reading the source code to the
official Firefox addon, as well as monitoring the site's HTTP activity.

You can check out the code here:

https://github.com/Komodo/kopy.io-addon

Recorded HTTP requests to and responses from kopy.io are available in this code
repository.

The documentation for Crypto-JS, as well as the source code, is available here:

https://code.google.com/p/crypto-js/

-------------------------------------------------------------------------------

## Security of kopy.io

Because of issues with JavaScript cryptography and kopy.io's HTTPS support
(see below), it is not reccomended you use kopy.io in the hopes of thwarting
non-trivial adversaries; a savvy attacker could embed malicious javascript
which exfiltrated the encryption key and/or plaintext when you visited the
site.

However, if your concern is that you don't want the individuals who monitor
pastebin sites to see your message, but you are not exchanging state secrets,
this may be the tool for you.

## HTTPS support

The kopy.io domain does not have its own certificate at this time, and
attemptiong to access it over HTTPS will raise a certificate error. Therefore
it is quite likely people will not use HTTPS, and that they will be susceptible
to attackers inserting JavaScript into the page to capture its content after
it has been decrypted.

## Accessing documents from the browser

Documents are linked in the folowing format:

https://kopy.io/<id>(#AES-Passphrase)

If the AES key is not supplied, and the document is encrypted,
the user will be prompted for it.

## API

* Response from the API are in JSON
* Creating & retrieving documents all happens with kopy.io/documents

## Creating documents

Send a POST request to kopy.io/documents with the following parameters:

* A valid Content-length header and a Content-type of
  application/x-www-form-urlencoded
* data: Your paste. If encrypted, it should be formatted in base 64
* language: Programming language for syntax highlightining; see "Languages" 
  for a listing.
* scheme: The theme kopy.io will use to render your paste; see "Schemes" for a
  listing.
* keep: Number of seconds until the document is deleted. The maximum (advertised)
  is one month (86400 seconds).
* security: Either "default" if the content is plain-text, or "encrypted".

* If all goes well, the server will respond with a 200 OK, a content type of
  application/json, and a JSON object with a "key" 
* There are several other parameters used by the front end, regarding things
  like font preferences. For now, I'm ignoring them.

## Retrieving documents

Send a GET request to kopy.io/documents/<id>.

If all goes well, you'll recieve a JSON object with a data element containing
the document and a security element which will be "default" if the data is
plaintext and "encrypted" if the data is not. Encrypted data will be represented
in the base 64 format.

If the document does not exist, you will recieve an object with a "message"
element and the value "Document not found".

## Cryptography

kopy.io uses Crypto-JS's with default settings; that is to say, AES-256-CBC.

The passphrase is used to derive a key and IV in the same manner as OpenSSL.
The method is documented here:

https://www.openssl.org/docs/crypto/EVP_BytesToKey.html

## Quirks

* kopy.io doesn't care if you give a paste a > 1mo lifetime
* kopy.io will store any data you POST to its API -- even if the paste is malformed,
  or a parameter isn't used by the app.
  * My theory is this is a holdover from Hastebin, where anything you POST to
   /documents is your paste verbatim
  * This means a few things:
    * A successful response doesn't mean a successful paste
    * Steganography -- our real paste is in the metadata!
    * We can use custom metadata to specify different ciphers

## Languages

* -1 (Auto Detect)
* C
* C++
* CoffeeScript
* CSS
* diff
* Go
* HTML
* Java
* JavaScript
* JSON
* Markdown
* LESS
* Perl
* PHP
* Python
* Ruby
* Sass
* SCSS
* Shell
* SQL
* XML
* APL
* Asterisk
* Cobol
* C#
* Clojure
* Common Lisp
* Cypher
* D
* DTD
* Dylan
* ECL
* Eiffel
* Erlang
* Fortran
* F#
* Gas
* Gherkin
* GitHub Flavored Markdown
* Groovy
* HAML
* Haskell
* Haxe
* ASP.NET
* Embedded Javascript
* JavaServer Pages
* HTTP
* Jade
* JSON-LD
* TypeScript
* Jinja2
* Julia
* Kotlin
* LiveScript
* Lua
* mIRC
* Modelica
* Nginx
* NTriples
* OCaml
* Octave
* Pascal
* PEG.js
* Pig
* Properties files
* Puppet
* Cython
* R
* reStructuredText
* Rust
* Scala
* Scheme
* Sieve
* Smalltalk
* SmartyMixed
* Solr
* SPARQL
* MariaDB
* sTeX
* LaTeX
* Tcl
* Tiki wiki
* TOML
* Turtle
* VB.NET
* VBScript
* Velocity
* Verilog
* XQuery
* YAML

## Schemes

Scheme Value  : Scheme Name

* "base16-default.dark"  :  Default
* "base16-3024.dark"  :  3024 Dark
* "base16-3024.light"  :  3024 Light
* "base16-ashes.dark"  :  Ashes Dark
* "base16-ashes.light"  :  Ashes Light
* "base16-atelierdune.dark"  :  Atelierdune Dark
* "base16-atelierdune.light"  :  Atelierdune Light
* "base16-atelierforest.dark"  :  Atelierforest Dark
* "base16-atelierforest.light"  :  Atelierforest Light
* "base16-atelierheath.dark"  :  Atelierheath Dark
* "base16-atelierheath.light"  :  Atelierheath Light
* "base16-atelierlakeside.dark"  :  Atelierlakeside Dark
* "base16-atelierlakeside.light"  :  Atelierlakeside Light
* "base16-atelierseaside.dark"  :  Atelierseaside Dark
* "base16-atelierseaside.light"  :  Atelierseaside Light
* "base16-bespin.dark"  :  Bespin Dark
* "base16-bespin.light"  :  Bespin Light
* "base16-brewer.dark"  :  Brewer Dark
* "base16-brewer.light"  :  Brewer Light
* "base16-chalk.dark"  :  Chalk Dark
* "base16-chalk.light"  :  Chalk Light
* "base16-codeschool.dark"  :  Codeschool Dark
* "base16-codeschool.light"  :  Codeschool Light
* "base16-default.dark"  :  Default Dark
* "base16-default.light"  :  Default Light
* "base16-eighties.dark"  :  Eighties Dark
* "base16-eighties.light"  :  Eighties Light
* "base16-embers.dark"  :  Embers Dark
* "base16-embers.light"  :  Embers Light
* "base16-google.dark"  :  Google Dark
* "base16-google.light"  :  Google Light
* "base16-grayscale.dark"  :  Grayscale Dark
* "base16-grayscale.light"  :  Grayscale Light
* "base16-greenscreen.dark"  :  Greenscreen Dark
* "base16-greenscreen.light"  :  Greenscreen Light
* "base16-isotope.dark"  :  Isotope Dark
* "base16-isotope.light"  :  Isotope Light
* "base16-londontube.dark"  :  Londontube Dark
* "base16-londontube.light"  :  Londontube Light
* "base16-marrakesh.dark"  :  Marrakesh Dark
* "base16-marrakesh.light"  :  Marrakesh Light
* "base16-mocha.dark"  :  Mocha Dark
* "base16-mocha.light"  :  Mocha Light
* "base16-monokai.dark"  :  Monokai Dark
* "base16-monokai.light"  :  Monokai Light
* "base16-ocean.dark"  :  Ocean Dark
* "base16-ocean.light"  :  Ocean Light
* "base16-paraiso.dark"  :  Paraiso Dark
* "base16-paraiso.light"  :  Paraiso Light
* "base16-railscasts.dark"  :  Railscasts Dark
* "base16-railscasts.light"  :  Railscasts Light
* "base16-shapeshifter.dark"  :  Shapeshifter Dark
* "base16-shapeshifter.light"  :  Shapeshifter Light
* "base16-solarized.dark"  :  Solarized Dark
* "base16-solarized.light"  :  Solarized Light
* "base16-tomorrow.dark"  :  Tomorrow Dark
* "base16-tomorrow.light"  :  Tomorrow Light
* "base16-twilight.dark"  :  Twilight Dark
* "base16-twilight.light"  :  Twilight Light
