@echo off
cd /d "%~dp0.."
echo Keeping the OSCE API awake. Leave this window open.
echo Closing it lets Render's free plan sleep the API again.
node scripts\keep-awake.mjs
pause
