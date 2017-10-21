#!/bin/bash

################################################################################
# dmine installer for Linux distros using pyinstaller.
#
# This script does the following:
#  1. Installs dmine using pyinstaller to ./builds/linux directory.
#  2. Create a symbolic link to run the dmine executable system wide.
#
# Usage:
#  build_linux.sh [output_directory]
################################################################################

##################################################
# Installing.
##################################################

# The base name of the executable file is "dmine".
name="dmine"
project_dir="$PWD"
build_path="./dmine"
out_dir="$PWD"
if [ ! -z "$1" ]; then
    out_dir=$1
fi

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

# Check file existence. Throw error if file not found.
function check_file {
    if [ ! -f $1 ]; then
        echo "Error: $1 is required for packaging, but it doesn't exist." 1>&2
        exit 1
    fi
}

# Add paths for imports.
add_path "$project_dir/src"
add_path "$project_dir/dep-py"

# Build the arguments.
add_arg "--noconfirm --log-level=WARN"
add_arg "--onedir" 
add_arg "--clean"
add_arg "--paths=$paths"
add_arg "--add-data=$project_dir/src/spiders:./spiders/"
add_arg "--additional-hooks-dir=$project_dir/hooks"
add_arg "--distpath=."
add_arg "--name=$name"
add_arg "$project_dir/src/main.py "
while read -r line; do # Add all spiders.
    add_arg "$line "
done < <(find ./src/spiders/ -maxdepth 1 -type f | grep -v __init__.py)

# Run pyinstaller.
pyinstaller ${arguments[@]}

# Remove temp dir created by pyinstaller.
rm -rf "./build"

# Move the .spec file to build dir.
mv $name.spec $build_path

##################################################
# Packaging.
##################################################

# Ensure the files for linux package exists.
check_file "./installer/linux/installer_linux.sh"
check_file "./installer/linux/uninstaller_linux.sh"

# Create the readme file for the package.
echo "Run install.sh to install dmine." > readme.txt
cp ./installer/linux/installer_linux.sh ./install.sh

# Remove the dmine_pkg directory if it already exists.
if [ -d "./dmine_pkg" ]; then
    rm -rf "./dmine_pkg"
fi

# Remove the dmine_linux.zip file if it already exists.
if [ -f "./dmine_linux.zip" ]; then
    rm "./dmine_linux.zip"
fi

# Create a dmine_pkg folder to put all the installation directories
# and files inside it before compress it.
mkdir "./dmine_pkg"
mv "$build_path" "./dmine_pkg"
mv install.sh "./dmine_pkg"
mv readme.txt "./dmine_pkg"
zip -r dmine_linux.zip "./dmine_pkg"
chmod 755 dmine_linux.zip

# Move the zip package to desired dir path (if specified).
echo "dmine_linux.zip saved at '$out_dir'."
if [ ! -z "$1" ]; then
    mv dmine_linux.zip $1
fi

# Clean up.
rm -rf "./dmine_pkg"

