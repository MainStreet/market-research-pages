@echo off
REM Create junctions for the consolidated MStreet-Global-Pages structure.
REM Each plugin's Output-Pages becomes a junction into the corresponding subfolder.
REM Idempotent: if a junction already exists at the target path, it will fail
REM that line — remove first if you need to re-run.

setlocal

set "PAGES_ROOT=C:\Users\ji\Desktop\MStreet-Global-Pages"

echo Creating Market-Data-Analysis junction...
mklink /J "C:\Users\ji\Desktop\Market-Data-Analysis-Plugins\Output-Pages" "%PAGES_ROOT%\Market-Data-Analysis"
if errorlevel 1 echo   FAIL

echo Creating Track-Follow-Analyze junction...
mklink /J "C:\Users\ji\Desktop\Track-Follow-Analyze-Plugins\Output-Pages" "%PAGES_ROOT%\Track-Follow-Analyze"
if errorlevel 1 echo   FAIL

echo.
echo Done. Verify with:
echo   dir /AL C:\Users\ji\Desktop\Market-Data-Analysis-Plugins
echo   dir /AL C:\Users\ji\Desktop\Track-Follow-Analyze-Plugins

endlocal
