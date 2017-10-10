#!/bin/bash

#
# dmine installer for Linux distros using pyinstaller.
#
# Use this to build the folder containing an executable binary file
# to run dmine together its data files and libraries.


# Base name of the executable file.
name="dmine"

install_path="/opt"

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

# Install.
echo "Installing $name to '$install_path'"
pyinstaller ${arguments[@]}

# Create symbolic link to the executable file at /usr/local/bin.
# If the symbolic link already exists, delete it before creating
# the link.
echo "Attempting to create the symbolic link '/usr/local/bin/$name'"
if [[ -L "/usr/local/bin/$name"  ]]; then
    echo "The symbolic link already exist. Deleting it now."
    rm "/usr/local/bin/$name"
fi
ln -s "$install_path/$name/$name" "/usr/local/bin/dmine"
echo "Finished creating the symbolic link."

# Move the .spec file to build dir.
mv $name.spec $install_path

if [[ -d build ]]; then
    rm -rf build
fi

echo "Installation successful. Please run 'dmine -h' to ensure."
