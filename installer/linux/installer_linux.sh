# 
# This file belongs to dmine_linux.zip package.
#

function expect {
    if [ ! -d $1 ] && [ ! -f $1 ]; then
        echo "Error: Installer expects $1 (a file or directory) in the"\
             "current directoru ($PWD)." 1>&2
        exit -1
    fi
}

# Integrity check: dep-bin and dmine directories must exists in the same
# directory as this installer.
dep_bin="dep-bin"
build_path="dmine"
shortcut="shortcut.sh"
expect $dep_bin
expect $build_path
expect $shortcut

# Test if a dmine folder already exist. If it exists, prompt the user
# to delete the existing dmine directory and make a new install.
reply=0
if [ -d /opt/dmine ]; then
    echo "Warning: A directory called dmine already exists in /opt."\
         "Do you want to delete this existing directory to install dmine?"\
         "(y/n)"
    while true;
    do
        read reply
        if [[ $reply == 'y' ]] || [[ $reply == 'n'  ]]; then
            break
        else
            echo "Invalid reply. Please enter either 'y' or 'n'."
        fi
    done
fi

if [[ $reply == 'n' ]]; then
    echo "Aborting installation."
    exit 0
fi

# Copy the linux build to /opt.
echo "==> Installing to '/opt/dmine'."
if [[ $reply == 'y' ]] || [[ $reply == 0  ]]; then
    sudo cp -r $build_path /opt/dmine
    sudo cp -r $dep_bin /opt/dmine
fi

if [ -d "/opt/$build_path" ]; then
    echo "Success."
else
    echo "Failed."
    exit -1
fi

# Create shortcut script to the executable file at /usr/local/bin
shortcut_path="/usr/local/bin/dmine"
echo "==> Creating a shortcut to '$shortcut_path'."
if [ -f $shortcut_path ]; then
    echo "Shortcut already exists. Removing it to create a new one."
    sudo rm $shortcut_path
fi
sudo cp $shortcut $shortcut_path

if [ -f $shortcut_path ]; then
    echo "Success."
else
    echo "Failed."
    exit -1
fi

# Finish.
echo "==> Installation finished. Please run 'dmine' to ensure successful "\
     "installation."
