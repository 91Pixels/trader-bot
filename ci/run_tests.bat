@echo off
REM Quick test runner for Windows
REM Run this file to execute all tests and generate HTML report

echo ========================================
echo BTC Trading Bot - Test Suite
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Creating test-reports directory...
if not exist "test-reports" mkdir test-reports
echo.

echo Running all tests...
python tests/run_all_tests.py

echo.
echo ========================================
echo Test execution complete
echo ========================================
echo.
echo Opening HTML report...
start test-reports\test_report_latest.html

pause
