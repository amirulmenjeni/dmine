#!/bin/bash

# Remove dmine install directory if it already exists.
if [ -d ./dmine ]; then
    rm -rf ./dmine
fi

# Remove dmine package if it already exists.
if [ -f ./dmine_linux.zip ]; then
    rm ./dmine_linux.zip
fi

# Install dmine using dmine.spec.
pyinstaller --distpath=./dmine dmine.spec

# Move the binary dependency directory up by one directory.
mv ./dmine/dmine/dep-bin/ ./dmine/

# Copy the linux installer shell script into the package directory.
if [ ! -f ./installer/linux/installer_linux.sh ]; then
    echo "Linux installer script for dmine not found. Aborting packaging."
    exit -1
fi
cp ./installer/linux/installer_linux.sh ./dmine/install.sh

# Copy the shortcut shell script into the package directory.
if [ ! -f ./installer/linux/shortcut.sh ]; then
    echo "Linux shortcut script for dmine not found. Aborting packaging."
    exit -1
fi
cp ./installer/linux/shortcut.sh ./dmine/shortcut.sh

# Create a brief readme for instruction to install.
echo "Please run install.sh to install dmine." > ./dmine/readme.txt

# Package in a zip file.
zip -r dmine_linux.zip ./dmine 
