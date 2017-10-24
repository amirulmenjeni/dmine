@echo off
title=Dmine Installer
rem Integrity check: dep-bin, dmine, schortcut.ch must be in one folder
set expected_file= dep-bin dmine shortcut.ch

(for %%a in (%expected_file%) do (
  CALL :expect %%a
))

:expect
IF EXIST "%~1" (
    EXIT /b 0
) ELSE (
    echo "Error: Installer expects %~1 (a file or directory)"
    EXIT /b 1
)

rem Checks if dmine folder exists in program files directory
if EXIST "%ProgramFiles%\Dmine" (
    echo "Warning: A directory called dmine already exists in ProgramFiles.
    Do you want to delete this existing directory to install dmine?"

       :validate_response
       set /p reply="[y/n]? "
       if /I "%reply%"=="y" (
          del /S "%ProgramFiles%/Dmine\*"
          goto unload_copy
       )
       if /I "%reply%"=="n" (
          echo "Aborting installation."
          set "reply="
          EXIT /b 1
       ) else (
          echo "Please enter a valid response"
          set "reply="
          goto validate_response
       )
)

echo "==> Installing to '/Program Files/dmine'."
MD "%ProgramFiles%/Dmine"
:unload_copy
xcopy /S /E "Dmine" "%ProgramFiles%/Dmine"
xcopy /S /E "dep-bin" "%ProgramFiles%/Dmine"

if EXIST "%ProgramFiles%/Dmine" (
  echo "Success."
) else (
  echo "Failed."
  EXIT /b 0
)
:: Create shortcut script to the executable file at USERPROFILE/Desktop
shortcut_path="%USERPROFILE%\Desktop"
echo "==> Creating a shortcut to '%shortcut_path%'."




:: Finish.
echo "==> Installation finished. Please run 'dmine' to ensure successful "\
     "installation."
