#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script maestro para ejecutar TODAS las pruebas del Cripto-Bot
Ejecuta todas las pruebas en la carpeta tests/
"""

import unittest
import sys
import os


def run_all_tests():
    """Descubrir y ejecutar todas las pruebas"""
    print("\n" + "="*70)
    print("EJECUTANDO SUITE COMPLETA - TODAS LAS PRUEBAS")
    print("="*70)
    print("Buscando pruebas en carpeta tests/...")
    
    # Descubrir todas las pruebas en tests/
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test*.py')
    
    # Contar tests
    def count_tests(suite_or_test):
        """Contar recursivamente el número de tests"""
        try:
            # Si es una suite, contar recursivamente
            return sum(count_tests(test) for test in suite_or_test)
        except TypeError:
            # Si es un test individual, contar como 1
            return 1
    
    total_tests = count_tests(suite)
    print(f"Total de pruebas encontradas: {total_tests}")
    print("="*70)
    print()
    
    # Ejecutar con verbosidad 2
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN FINAL DE TODAS LAS PRUEBAS")
    print("="*70)
    print(f"Total ejecutadas: {result.testsRun}")
    print(f"Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print(f"Omitidas: {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("\nTODAS LAS PRUEBAS PASARON")
        print("Sistema completamente validado para operar en modo LIVE")
        return 0
    else:
        print("\nALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores antes de operar en modo LIVE")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
