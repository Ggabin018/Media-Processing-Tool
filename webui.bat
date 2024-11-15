@echo off

call .\venv\Scripts\deactivate.bat
call .\venv\Scripts\activate.bat

if %errorlevel% equ 0 (
    IF /i "%comspec% /c %~0 " equ "%cmdcmdline:"=%" (
        REM echo This script was started by double clicking.
        cmd /k python.exe src/main.py %*
    ) ELSE (
        REM echo This script was started from a command prompt.
        python.exe src/main.py %*
    )
)