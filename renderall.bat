@echo off

set PYTHONUNBUFFERED=on
php renderall.php %* 2>&1 1>NUL
