@echo off

call python -m virtualenv venv
call .\venv\Scripts\activate.bat
call pip install -r requirements.txt
call .\venv\Scripts\deactivate.bat