@echo off
title /unium grabber - Installing Requirements..
echo.
echo [i] Installing required python packages from requirements.txt...
echo.

pip install -r requirements.txt

cls
title /unium grabber - Installation complete!
echo.
echo [!] Python packages successfully installed.
echo.
timeout /t 4 >nul

cls
title /unium grabber - Token / Prefix
echo.
echo [i] Please make sure your bot token is set in the grabber.py file. 
echo [i] Same with your command prefix of choice.
echo.
echo [i] Press enter when ready.
pause >nul

cls
title /unium grabber - Building Executable..
echo.
echo [i] Started building executable..
echo.

REM Feel free to adjust this to your liking
pyinstaller --onefile --noconsole grabber.py

cls
title /unium grabber - Build complete!
echo.
echo [!] Executable built successfully.
echo [i] Thanks for using unium grabber!
echo.
pause