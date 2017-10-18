echo "Run install.sh to install dmine." > readme.txt
cp ./installer_linux.sh ./install.sh
zip -r dmine_linux.zip ./builds/linux/dmine install.sh readme.txt
rm install.sh
rm readme.txt
chmod 755 dmine_linux.zip
