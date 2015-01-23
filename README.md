BERT
----
Simple *B*it *e*rror-*r*ate *t*ester. Implemented in Python for convience, but the wire protocol
should be simple enough to implement in other language.

Why
===
Serial communication channels, while simple, can be notoriously difficult to install and/or operate
error free. There are many subtle pitfalls and mistakes that can compromise a link's ability to pass
data. Did you terminate that RS-485 network? Is that network stub too long? Are your transmission
lines well isolated from sources of noise? Are reflections turning that '1' into a '0'? Well, BERT
*won't* prevent you making such errors, but it *will* help you quickly identify and characterize 
any transmission errors that are occuring.

Features
========
 * Variable input streams types. Should be easy enough to implement additional streams. 
 * Configurable block sizes. Stream data down from a single byte, to 65535 bytes per transaction.
 * Configurable turnaround.
 * Simple checksumming. Identify errors in transactions quickly and easily.
 
Future
======
Right now, you just run it, and let it go for awhile. Would be nice (and hopefully) easy to add support
for defining test parameters (durations, total size, finite data source, etc)

Usage
=====
Coming soon.™
