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

paths=""
function add_path {
    semicolon=""
    if [[ $paths != "" ]]; then
        semicolon=":" 
    fi
    paths=$paths$semicolon$1
}

function auto_add_paths {
    while read -r line;
    do
        add_path $line
    done < <(find $1 -type d | grep -v "__pycache__$"\
                             | grep -v "dist-info$")
}

hidden_import_args=""
function add_hidden_import {
    arg="--hidden-import=$1 "
    hidden_import_args=$hidden_import_args$arg
}

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
add_arg "--additional-hooks-dir=./hooks"
add_arg "--add-data=./src/README.md:."
add_arg "--add-data=./src/spiders:./spiders/"
add_arg "--distpath=$install_path"
add_arg "--name=$name"
add_arg "./src/main.py "
while read -r line; do # Add all spiders.
    add_arg "$line "
done < <(find ./src/spiders/ -maxdepth 1 -type f | grep -v __init__.py)

echo "Installing dmine at: $install_path"
/bin/pyinstaller ${arguments[@]}

if [[ -d build ]]; then
    rm -rf build
fi
