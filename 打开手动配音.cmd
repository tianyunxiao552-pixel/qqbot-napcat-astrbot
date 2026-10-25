@echo off
set "version=v2ProPlus"
set "PYTHONUTF8=1"
if not exist "%~dp0GPT-SoVITS\go-webui.bat" (
  echo Install GPT-SoVITS under this folder first. See README.md.
  pause
  exit /b 1
)
cd /d "%~dp0GPT-SoVITS"
call go-webui.bat
