#!/bin/bash

# dmine installer for Linux distros using pyinstaller.
#
# This script does the following:
#  1. Installs dmine using pyinstaller to ./builds/linux directory.
#  2. Create a symbolic link to run the dmine executable system wide.

# Base name of the executable file.
name="dmine"

install_path="$PWD/builds/linux"

# Use this method to add paths for pyinstaller.
paths=""
function add_path {
    semicolon=""
    if [[ $paths != "" ]]; then
        semicolon=":" 
    fi
    paths=$paths$semicolon$1
}

# Use this method to add arguments to pass to the pyinstaller.
declare -a arguments
function add_arg {
    arguments+=($1)
}

# Add paths for imports.
add_path "./src"
add_path "./dep-py"

if [[ -d dist ]]; then
    rm -rf dist
fi

# Build the arguments.
add_arg "--noconfirm --log-level=WARN"
add_arg "--onedir" 
add_arg "--clean"
add_arg "--paths=$paths"
add_arg "--add-data=./src/spiders:./spiders/"
add_arg "--additional-hooks-dir=./hooks"
add_arg "--distpath=$install_path"
add_arg "--name=$name"
add_arg "./src/main.py "
while read -r line; do # Add all spiders.
    add_arg "$line "
done < <(find ./src/spiders/ -maxdepth 1 -type f | grep -v __init__.py)

# Run pyinstaller.
pyinstaller ${arguments[@]}

# Move the .spec file to build dir.
mv $name.spec $install_path
