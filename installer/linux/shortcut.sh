#!/bin/bash

# This shortcut will create a temporary sym link
# to the dmine executable binary to allow user to run dmine while
# having access to its binary dependencies.

# Check if a file or dir named 'dmine' exists.
# If it does, then rename the file/dir temporarily.
if [ -f dmine ] || [ -d dmine ]; then
    mv dmine .__temp_dmine__
fi

# Create a temporary sym link.
ln -s /opt/dmine/dmine/dmine ./dmine
./dmine "$@"

# Remove the temporary sym link.
if [ -L dmine ]; then
    rm dmine
fi

# Rename back the renamed file/dir, if it exists.
if [ -f .__temp_dmine__ ] || [ -d .__temp_dmine__ ]; then
    mv .__temp_dmine__ dmine
fi
