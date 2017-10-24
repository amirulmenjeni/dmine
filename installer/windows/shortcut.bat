@echo off

set shortcut_path=%USERPROFILE%\.dmine
DOSKEY dmine="%ProgramFiles%\Dmine\Dmine\Dmine.exe" $*
DOSKEY cd_dmine=cd %ProgramFiles%\Dmine\Dmine

