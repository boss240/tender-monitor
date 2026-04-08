@echo off
chcp 65001 >nul
echo ===================================
echo  УЗЕ Tender Scanner - Локальний запуск
echo ===================================
echo.

cd /d "%~dp0"

REM Завантажити змінні з .env (якщо є)
if exist .env (
    for /f "tokens=1,* delims==" %%A in (.env) do (
        set "%%A=%%B"
    )
)

python scanner.py %*

echo.
pause
