#!/bin/bash
ln -s /opt/dmine/dmine/dmine ./dmine
./dmine "$@"
if [ -L ./dmine ]; then
    rm ./dmine
fi
