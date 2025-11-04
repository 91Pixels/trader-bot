@echo off
echo ======================================================================
echo EJECUTANDO TODAS LAS PRUEBAS DEL CRIPTO-BOT
echo ======================================================================
echo.

python run_all_tests.py

if %ERRORLEVEL%==0 (
    echo.
    echo ======================================================================
    echo RESULTADO: TODAS LAS PRUEBAS PASARON
    echo ======================================================================
    echo.
    echo Sistema completamente validado para operar en modo LIVE
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo ======================================================================
    echo RESULTADO: ALGUNAS PRUEBAS FALLARON
    echo ======================================================================
    echo.
    echo NO operes en modo LIVE hasta resolver los problemas
    echo.
    pause
    exit /b 1
)
