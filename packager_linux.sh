function check_file {
    if [ ! -f $1 ]; then
        echo "Error: $1 is required for packaging, but it doesn't exist." 1>&2
        exit 1
    fi
}

check_file "build_linux.sh"
check_file "installer_linux.sh"
bash -c ./build_linux.sh

echo "Run install.sh to install dmine." > readme.txt
cp ./installer_linux.sh ./install.sh
zip -r dmine_linux.zip ./builds/linux/dmine install.sh readme.txt
rm install.sh
rm readme.txt
chmod 755 dmine_linux.zip
