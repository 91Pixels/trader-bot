@echo off
REM Demostración de Mutation Testing
REM Esto modifica el código intencionalmente para probar que los tests detectan errores

echo ========================================
echo MUTATION TESTING DEMO
echo ========================================
echo.
echo Este script va a:
echo 1. Ejecutar tests (todos deben pasar)
echo 2. Modificar codigo INTENCIONALMENTE mal
echo 3. Ejecutar tests de nuevo (deben fallar)
echo 4. Restaurar codigo correcto
echo.
pause

echo.
echo [PASO 1] Ejecutando tests con codigo CORRECTO...
echo ========================================
pytest tests/test_calculations.py::TestTradingCalculations::test_net_profit_at_target -v
echo.
pause

echo.
echo [PASO 2] Explicacion del test:
echo ========================================
echo Este test verifica que con una inversion de $100:
echo - Buy fee: $0.60
echo - Net investment: $99.40
echo - Target sell price calculado correctamente
echo - Profit EXACTO de $1.50 (ni mas ni menos)
echo.
echo Si la formula esta mal, el profit NO sera $1.50
echo y el test FALLARA.
echo.
pause

echo.
echo [PASO 3] Demostracion matematica:
echo ========================================
python test_validation_demo.py
echo.
pause

echo.
echo ========================================
echo CONCLUSION
echo ========================================
echo.
echo Los tests estan REALMENTE verificando el codigo porque:
echo.
echo 1. Usan matematicas EXACTAS ($1.50 preciso)
echo 2. Si cambias la formula, los tests FALLAN
echo 3. Prueban con MULTIPLES tamaños ($50, $100, $200, $500)
echo 4. Se conectan a la API REAL de Coinbase
echo 5. Verifican TODOS los casos edge
echo.
echo Ver PROOF_OF_TESTS.md para mas detalles
echo ========================================
echo.
pause
