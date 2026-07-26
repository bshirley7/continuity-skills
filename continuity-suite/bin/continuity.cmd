@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CONTINUITY_PYTHON_FILE=%~dp0..\..\..\.continuity\private\python-interpreter.txt"
set "CONTINUITY_PYTHON="
if exist "%CONTINUITY_PYTHON_FILE%" set /p CONTINUITY_PYTHON=<"%CONTINUITY_PYTHON_FILE%"
if not defined CONTINUITY_PYTHON goto py_launcher
if not exist "%CONTINUITY_PYTHON%" goto py_launcher
"%CONTINUITY_PYTHON%" "%~dp0continuity" %*
exit /b %errorlevel%

:py_launcher
where py.exe >nul 2>nul
if errorlevel 1 goto python_launcher
py.exe -3 "%~dp0continuity" %*
exit /b %errorlevel%

:python_launcher
python.exe "%~dp0continuity" %*
exit /b %errorlevel%
