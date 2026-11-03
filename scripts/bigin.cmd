@echo off
REM Windows launcher for the Bigin engine (lib/bigin). Stdlib Python 3.9+ only.
REM UTF-8 so child Python prints (→, —) and JSON don't crash under cp1252 consoles.
REM Forward %* without EnableDelayedExpansion so ! in paths is not stripped.
setlocal DisableDelayedExpansion
set PYTHONUTF8=1
set "CLI=%~dp0..\lib\bigin\cli.py"
where py >nul 2>&1
if not errorlevel 1 goto _run_py
where python3 >nul 2>&1
if not errorlevel 1 goto _run_python3
where python >nul 2>&1
if not errorlevel 1 goto _run_python
echo bigin.cmd: need py -3, python3, or python on PATH >&2
exit /b 1

:_run_py
py -3 "%CLI%" %*
exit /b %ERRORLEVEL%

:_run_python3
python3 "%CLI%" %*
exit /b %ERRORLEVEL%

:_run_python
python "%CLI%" %*
exit /b %ERRORLEVEL%
