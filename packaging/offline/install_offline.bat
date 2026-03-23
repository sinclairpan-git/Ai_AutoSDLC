@echo off
setlocal

set "ROOT=%~dp0"
set "POWERSHELL_EXE=powershell"
if exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%install_offline.ps1" %*
if errorlevel 1 (
  echo Offline install failed.
  exit /b 1
)

echo Offline install complete.
exit /b 0
