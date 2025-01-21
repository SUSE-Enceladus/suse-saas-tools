#!/bin/bash
set -ex

# Setup python3 link
rm -f /usr/bin/python3
ln -s /usr/bin/python3.11 /usr/bin/python3
