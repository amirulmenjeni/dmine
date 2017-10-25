@echo off

:: Remove dmine install directory if it already exists.
if exist "dmine_windows" (
	echo lol
	del /S /Q "dmine_windows"
)

if exist "dmine_windows.zip" (
	del /Q "dmine_windows.zip"
)

:: Install dmine using dmine.spec.
pyinstaller --distpath=dmine_windows dmine.spec

:: Move the binary dependency directory up by one directory.
move dmine_windows/dmine/dep-bin dmine_windows

if not exist "installer\windows\installer_windows.bat" (
	 echo "Windows installer script for dmine not found. Aborting packaging."
	 EXIT /b 1
)

copy "installer\windows\installer_windows.bat" "dmine_windows\"

:: Create a brief readme for instruction to install.
echo "Please run install_windows.bat to install dmine." > dmine_windows\readme.txt


