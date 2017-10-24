@echo off

set shortcut_path=%USERPROFILE%/.dmine
cmd.exe /K %shortcut_path%/shortcut.bat
DOSKEY dmine=%ProgramFiles%/Dmine/Dmine/Dmine.exe
DOSKEY cd_dmine=cd %ProgramFiles%/Dmine/Dmine/ ::change directory to dmine build path