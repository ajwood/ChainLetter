# Overview

The Chainletter system is built to be open, without using login accounts. It's
designed to have simple protections, so that not just anyone can add/edit. Only
people who have received an official invitation can contribute.

## Hashes

Chainletter entries are added and tracked with
[hashes](https://en.wikipedia.org/wiki/Cryptographic_hash_function)
([sha256](https://en.wikipedia.org/wiki/SHA-2)). In addition to acting as an
index for the Chainletter entries and links, they serve an authorization
mechanism. Partial hashes can be used for normal access (any n-character prefix,
enough to uniquely identify a hash), and a full hash grants you write access.

When someone shares a hash with you, you use it to _login_ to the system. It
must be a full hash (all 64 characters), and only you and the person who gave it
to should know it. Since you have the full hash, you'll be able to write a
letter to associate with it. After adding the letter, you'll be able to generate
new hashes (up to five) to share with others.