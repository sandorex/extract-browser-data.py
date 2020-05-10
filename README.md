# extract-browser-data.py
Python library to extract data from browsers (only chromium and firefox based ones)

This project has been abandoned in favor of [GO rewrite](https://github.com/sandorex/ebd)

> **WARNING: this library is in it's alpha stage**

## Cross-Browser Compatability
- Reading extensions
- Reading history
- Reading bookmarks
- Reading cookies _(limited on chromium due to encryption)_

#### Firefox Only
- Reading containers
- Reading last session _(WIP on chromium)_
- Reading account info

## TODO

- Last session on chromium, reading the `SNSS` format
- Try to decrypt cookie value from chromium
- Writing any kind of data
- Testing, testing and more testing..
- Documentation... a lot of documentation..
- Testing the tampering protection in chromium
