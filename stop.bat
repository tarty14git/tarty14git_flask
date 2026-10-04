@echo off
echo Stopping CTH Enterprise Flask Application...
taskkill /F /IM waitress-serve.exe 2>NUL
taskkill /F /FI "WINDOWTITLE eq CTH Enterprise*" 2>NUL
echo Application stopped.
