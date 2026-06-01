@echo off
REM ============================================================================
REM  fusion-bridge-up.cmd  -  one-click Fusion MCP bridge bring-up (Windows host)
REM ----------------------------------------------------------------------------
REM  Self-elevates to Administrator, applies the netsh portproxy + firewall
REM  bridge (idempotent), then reports whether port 9876 is actually listening.
REM
REM  NOTE: this does NOT start the Fusion add-in. Fusion 360 must be open with
REM  the MCP add-in running for 9876 to listen - the bridge only forwards to it.
REM ============================================================================

setlocal
set PORT=9876
set SCRIPTDIR=%~dp0

REM --- self-elevate to admin if not already ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo === Applying Fusion MCP bridge (port %PORT%) ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPTDIR%fusion-mcp-bridge.ps1" -Port %PORT%

echo.
echo === Checking port %PORT% ===
powershell -NoProfile -Command ^
  "$c = Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue;" ^
  "if ($c) { Write-Host 'OK: port %PORT% is LISTENING - bridge + add-in are up.' -ForegroundColor Green }" ^
  "else { Write-Host 'NOT LISTENING on %PORT%.' -ForegroundColor Yellow; Write-Host 'Start Fusion 360 and run the MCP add-in, then re-run this script.' -ForegroundColor Yellow }"

echo.
echo Next: relaunch Claude Code so the fusion MCP tools load, then /resume.
echo.
pause
endlocal
