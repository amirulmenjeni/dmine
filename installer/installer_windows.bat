@echo off

rem Integrity check: dep-bin, dmine, schortcut.ch must be in one folder
set expected_file= dep-bin dmine shortcut.ch

(for %%a in (%expected_file%) do (
  CALL :expect %%a
))

rem Checks if dmine folder exists in program files directory
if EXIST "%ProgramFiles%\Dmine" (
    echo "Warning: A directory called dmine already exists in \ProgramFiles."\
       "Do you want to delete this existing directory to install dmine?"\

       :validate_response
       SETLOCAL
       set /p reply=[y/n]?
       ENDLOCAL
       if %reply%==y %reply%==n (
          EXIT /b 1
       ) else (
          echo Please enter a valid response
          goto validate_response
       )
)
EXIT /b 0

:expect
IF EXIST "%~1" (
    EXIT /b 0
) ELSE (
    echo "Error: Installer expects %~1 (a file or directory)"
    EXIT /b 1
)
