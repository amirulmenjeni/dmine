#!/bin/bash

#
# dmine uninstaller for linux.
#

# Remove recursively the install dir.
install_dir="/opt/dmine"
if [[ ! -d $install_dir ]]; then
    echo "Error: The install directory '$install_dir' is not found. "\
         "Uninstallation failed." 1&>2
fi
rm -rf "/opt/dmine"

# Remove the sym link.
sym_link_path="/usr/local/bin/dmine"
if [[ ! -L $sym_link_path ]]; then
    echo "Error: The symbolic link '$sym_link_path' is not found. "\
         "Uninstallation failed." 1&>2
fi
rm $sym_link_path

echo "Finished uninstalling dmine."
