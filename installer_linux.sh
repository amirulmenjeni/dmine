# Expects ./builds/linux directory to exist.
if [ ! -d builds/linux/dmine ]; then
    echo "Error: Installer expects './builds/linux' directory in the "\
         "current directory ($PWD)." 1>&2
    exit 1
fi

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

# Copy the linux build to /opt.
echo "==> Installing to /opt/dmine"
if [[ $reply == 'y' ]] || [[ $reply == 0  ]]; then
    sudo cp -r ./builds/linux/dmine /opt
fi


# Create symbolic link to the executable file at /usr/local/bin.
echo "==> Attempting to create the symbolic link '/usr/local/bin/dmine'"
if [[ -L "/usr/local/bin/dmine"  ]]; then
    echo "The symbolic link already exist."
else
    ln -s "$/opt/dmine/dmine" "/usr/local/bin/dmine"
fi

# Finish.
echo "==> Installation finished. Please run 'dmine' to ensure successful "\
     "installation."
