#!/bin/bash

#
# dmine installer for Linux OS using pyinstaller.
#

install_path="./"
if [[ "$#" == 1 ]]; then
    install_path="$1" 
fi

# Base name of the executable file.
name="dmine"

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
add_path "./dep"

if [[ -d dist ]]; then
    rm -rf dist
fi

# Build the arguments.
add_arg "--noconfirm --log-level=WARN"
add_arg "--onedir" 
add_arg "--clean"
add_arg "--paths=$paths"
add_arg "--add-data=./src/README.md:."
add_arg "--add-data=./src/spiders:./spiders/"
add_arg "--additional-hooks-dir=./hooks"
add_arg "--distpath=$install_path"
add_arg "--name=$name"
add_arg "./src/main.py "
while read -r line; do # Add all spiders.
    add_arg "$line "
done < <(find ./src/spiders/ -maxdepth 1 -type f | grep -v __init__.py)

echo "Install directory: $install_path/$name"
pyinstaller ${arguments[@]}

echo "Creating symbolic link of the executable in /usr/local/bin."
ln -s "$install_path/$name/$name" "/usr/local/bin/$name" 
if [[ $? != 0 ]]; then
    echo "Failed to create symbolic link."
    exit
fi

echo "Done! To check if dmine installed correctly, type 'dmine'"

if [[ -d build ]]; then
    rm -rf build
fi

