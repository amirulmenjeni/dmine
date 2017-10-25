@echo off
Title=Dmine installer 
set dep-bin=dep-bin
set build_path=Dmine
set shortcut=shortcut.bat

CALL :expect %dep-bin%
CALL :expect %build_path%
CALL :expect %shortcut%

:: Checks if dmine folder exists in program files directory
if EXIST "%ProgramFiles%\Dmine" (
    echo "Warning: A directory called dmine already exists in ProgramFiles. Do you want to delete this existing directory to install dmine?"
    goto validate_response

    :validate_response
    set /p reply="[Y | N]? "
    if /I "%reply%"=="y" (
       del /S /Q "%ProgramFiles%/Dmine\*"
       goto unload_copy
    )
    if /I "%reply%"=="n" (
       echo Aborting installation
       ::goto end
       EXIT /b 1
    ) else (
       echo "Please enter a valid response"
       goto validate_response
    )
)

echo "==> Installing to 'C:/Program Files/dmine'."

MD "%ProgramFiles%/Dmine"

:unload_copy
xcopy /O /X /E /H /K  "%build_path%" "%ProgramFiles%\Dmine\%build_path%\"
xcopy /O /X /E /H /K  "%dep-bin%" "%ProgramFiles%\Dmine\%dep-bin%\"

if EXIST "%ProgramFiles%/%build_path%" (
  echo "Build path Success."
) else (
  echo "Build path Failed."
  EXIT /b 0
)

:: Create shortcut script to the executable file at USERPROFILE/Desktop
set shortcut_path="%USERPROFILE%\.dmine"
echo "==> Creating a shortcut to '%shortcut_path%'."

if EXIST "%shortcut_path%" (
    echo "Shortcut already exists. Removing it to create a new one."
    del /Q /S "%shortcut_path%"
	goto skip
)

MKDIR "%shortcut_path%"

:skip
copy %shortcut% %shortcut_path%

if EXIST "%shortcut_path%" (
    echo "Success."
) else (
    echo "Failed."
    EXIT /b 0
)

:: copy reg keys for persistent dmine alias
:: Finish.
echo "==> Registering alias for Dmine..."

copy "reg_keys.reg" %shortcut_path%

reg import %shortcut_path%\reg_keys.reg

:: Finish.
echo "==> Installation finished. Please run 'dmine' to ensure successful installation."

goto end	 

:expect
IF EXIST "%~1" (
    EXIT /b 0
) ELSE (
    echo "Error: Installer expects %~1 (a file or directory)"
    EXIT /b 1
)

:End
