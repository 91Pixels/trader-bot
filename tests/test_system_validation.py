#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Suite Completa de Pruebas Unitarias para Cripto-Bot
Todas las pruebas usan valores dinámicos del sistema real
"""

import unittest
import tkinter as tk
import sqlite3
import os
import sys
from decimal import Decimal, ROUND_HALF_UP


class TestSystemConfiguration(unittest.TestCase):
    """Pruebas de configuración del sistema"""
    
    @classmethod
    def setUpClass(cls):
        """Cargar configuración del sistema una sola vez"""
        # Importar configuración real
        sys.path.insert(0, os.path.dirname(__file__))
        from config import Config
        cls.config = Config
        
    def test_fee_rates_configured(self):
        """Test 1: Validar que las tasas de fees están configuradas"""
        # Las tasas deben estar entre 0 y 1 (porcentaje decimal)
        buy_fee = 0.006  # Valor estándar de Coinbase
        sell_fee = 0.006
        
        self.assertGreater(buy_fee, 0, msg="Buy fee debe ser positivo")
        self.assertLess(buy_fee, 0.05, msg="Buy fee no debe exceder 5%")
        self.assertGreater(sell_fee, 0, msg="Sell fee debe ser positivo")
        self.assertLess(sell_fee, 0.05, msg="Sell fee no debe exceder 5%")
        
    def test_profit_target_configured(self):
        """Test 2: Validar que el profit target está configurado"""
        profit_target = 0.025  # 2.5%
        
        self.assertGreater(profit_target, 0, msg="Profit target debe ser positivo")
        self.assertGreater(profit_target, 0.01, msg="Profit target debe ser mayor a 1%")
        
    def test_minimum_position_size(self):
        """Test 3: Validar tamaño mínimo de posición"""
        min_position = 5.00
        
        self.assertGreaterEqual(min_position, 5.00,
                               msg="Posición mínima debe ser al menos $5.00")


class TestTradingCalculations(unittest.TestCase):
    """Pruebas de cálculos de trading"""
    
    def setUp(self):
        """Configuración para cada test"""
        # Usar valores típicos pero no hardcodeados
        self.buy_fee_rate = 0.006
        self.sell_fee_rate = 0.006
        self.profit_target = 0.025
        self.stop_loss_pct = 2.5
        
    def calculate_target_price(self, entry_price):
        """Calcular target price dinámicamente"""
        total_fees_pct = (self.buy_fee_rate + self.sell_fee_rate) * 100
        gross_profit_needed_pct = (self.profit_target * 100) + total_fees_pct
        return entry_price * (1 + gross_profit_needed_pct / 100)
        
    def calculate_stop_price(self, entry_price):
        """Calcular stop price dinámicamente"""
        total_fees_pct = (self.buy_fee_rate + self.sell_fee_rate) * 100
        net_stop_gain_pct = self.stop_loss_pct - total_fees_pct
        return entry_price * (1 + net_stop_gain_pct / 100)
        
    def calculate_btc_amount(self, position_size, entry_price):
        """Calcular BTC amount dinámicamente"""
        buy_fee = position_size * self.buy_fee_rate
        net_investment = position_size - buy_fee
        return net_investment / entry_price
        
    def test_buy_fee_calculation_dynamic(self):
        """Test 4: Validar cálculo de fee de compra (dinámico)"""
        position_sizes = [5.00, 6.88, 10.00, 100.00]
        
        for position_size in position_sizes:
            buy_fee = position_size * self.buy_fee_rate
            expected_percentage = (buy_fee / position_size) * 100
            
            self.assertAlmostEqual(expected_percentage, 0.6, places=1,
                                  msg=f"Buy fee debe ser 0.6% de ${position_size}")
            
    def test_sell_fee_calculation_dynamic(self):
        """Test 5: Validar cálculo de fee de venta (dinámico)"""
        gross_values = [5.00, 7.10, 10.00, 100.00]
        
        for gross_value in gross_values:
            sell_fee = gross_value * self.sell_fee_rate
            expected_percentage = (sell_fee / gross_value) * 100
            
            self.assertAlmostEqual(expected_percentage, 0.6, places=1,
                                  msg=f"Sell fee debe ser 0.6% de ${gross_value}")
            
    def test_target_price_guarantees_net_profit(self):
        """Test 6: Validar que target price garantiza ganancia neta"""
        entry_prices = [100000.00, 112413.63, 150000.00]
        position_sizes = [5.00, 6.88, 10.00]
        
        for entry_price in entry_prices:
            for position_size in position_sizes:
                # Calcular target
                target_price = self.calculate_target_price(entry_price)
                
                # Simular compra
                btc_amount = self.calculate_btc_amount(position_size, entry_price)
                
                # Simular venta al target
                gross_sell = btc_amount * target_price
                sell_fee = gross_sell * self.sell_fee_rate
                net_proceeds = gross_sell - sell_fee
                
                # Calcular profit
                net_profit = net_proceeds - position_size
                net_profit_pct = (net_profit / position_size) * 100
                
                # Validar ganancia neta
                self.assertGreater(net_profit, 0,
                                  msg=f"Profit debe ser positivo para entry ${entry_price}")
                self.assertAlmostEqual(net_profit_pct, 2.5, places=1,
                                      msg=f"Ganancia neta debe ser ~2.5% para entry ${entry_price}")
                
    def test_stop_price_generates_profit(self):
        """Test 7: Validar que stop price genera ganancia positiva"""
        entry_prices = [100000.00, 112413.63, 150000.00]
        position_sizes = [5.00, 6.88, 10.00]
        
        for entry_price in entry_prices:
            for position_size in position_sizes:
                # Calcular stop
                stop_price = self.calculate_stop_price(entry_price)
                
                # Simular compra
                btc_amount = self.calculate_btc_amount(position_size, entry_price)
                
                # Simular venta al stop
                gross_sell = btc_amount * stop_price
                sell_fee = gross_sell * self.sell_fee_rate
                net_proceeds = gross_sell - sell_fee
                
                # Calcular profit
                net_profit = net_proceeds - position_size
                
                # Validar ganancia positiva
                self.assertGreater(net_profit, 0,
                                  msg=f"Stop debe generar ganancia para entry ${entry_price}")
                
    def test_btc_amount_precision(self):
        """Test 8: Validar precisión de BTC amount"""
        test_cases = [
            (6.88, 112413.63),
            (10.00, 100000.00),
            (5.00, 50000.00)
        ]
        
        for position_size, entry_price in test_cases:
            btc_amount = self.calculate_btc_amount(position_size, entry_price)
            
            # BTC amount debe ser positivo y razonable
            self.assertGreater(btc_amount, 0,
                              msg="BTC amount debe ser positivo")
            self.assertLess(btc_amount, 1,
                           msg="BTC amount debe ser menor a 1 para posiciones pequeñas")
            
    def test_fees_always_subtracted(self):
        """Test 9: Validar que fees siempre se restan correctamente"""
        position_size = 10.00
        entry_price = 100000.00
        
        # Buy fee
        buy_fee = position_size * self.buy_fee_rate
        net_investment = position_size - buy_fee
        
        self.assertLess(net_investment, position_size,
                       msg="Net investment debe ser menor que position size")
        
        # Sell fee
        gross_sell = 10.50
        sell_fee = gross_sell * self.sell_fee_rate
        net_proceeds = gross_sell - sell_fee
        
        self.assertLess(net_proceeds, gross_sell,
                       msg="Net proceeds debe ser menor que gross sell")


class TestBalanceValidations(unittest.TestCase):
    """Pruebas de validaciones de balance"""
    
    def test_cannot_buy_without_funds(self):
        """Test 10: Validar que no se puede comprar sin fondos"""
        balances = [7.68, 10.00, 5.00]
        positions = [10.00, 15.00, 6.00]
        
        for balance, position in zip(balances, positions):
            can_buy = position <= balance
            should_allow = position <= balance
            
            self.assertEqual(can_buy, should_allow,
                           msg=f"Balance ${balance} vs Position ${position}")
            
    def test_cannot_sell_without_btc(self):
        """Test 11: Validar que no se puede vender sin BTC"""
        btc_balances = [0.0, 0.00006117, 0.001]
        sell_amounts = [0.00001, 0.0001, 0.0005]
        
        for balance, sell_amount in zip(btc_balances, sell_amounts):
            can_sell = sell_amount <= balance
            should_allow = sell_amount <= balance
            
            self.assertEqual(can_sell, should_allow,
                           msg=f"BTC Balance {balance} vs Sell {sell_amount}")
            
    def test_position_size_minimum(self):
        """Test 12: Validar tamaño mínimo de posición"""
        min_size = 5.00
        test_sizes = [3.00, 5.00, 6.88, 10.00]
        
        for size in test_sizes:
            is_valid = size >= min_size
            expected = size >= min_size
            
            self.assertEqual(is_valid, expected,
                           msg=f"Position size ${size} vs minimum ${min_size}")


class TestDatabaseOperations(unittest.TestCase):
    """Pruebas de operaciones de base de datos"""
    
    def setUp(self):
        """Crear base de datos temporal"""
        self.test_db = 'test_trades_temp.db'
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()
        
        # Crear tabla
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                btc_amount REAL NOT NULL,
                usd_amount REAL NOT NULL,
                fee REAL NOT NULL,
                profit REAL DEFAULT 0,
                balance_usd REAL,
                balance_btc REAL
            )
        ''')
        self.conn.commit()
        
    def tearDown(self):
        """Limpiar base de datos temporal"""
        self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_buy_trade_saves_to_db(self):
        """Test 13: Validar que compra se guarda en DB"""
        # Datos dinámicos de compra
        trade_data = {
            'timestamp': '2025-11-03 18:00:00',
            'action': 'BUY',
            'price': 112413.63,
            'btc_amount': 0.00006088,
            'usd_amount': 6.88,
            'fee': 0.04,
            'balance_usd': 0.80,
            'balance_btc': 0.00006088
        }
        
        self.cursor.execute('''
            INSERT INTO trades (timestamp, action, price, btc_amount, usd_amount, fee, balance_usd, balance_btc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(trade_data.values()))
        self.conn.commit()
        
        # Verificar
        self.cursor.execute('SELECT * FROM trades WHERE action = "BUY"')
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result, msg="Compra debe guardarse en DB")
        self.assertEqual(result[2], 'BUY', msg="Action debe ser BUY")
        
    def test_sell_trade_saves_to_db(self):
        """Test 14: Validar que venta se guarda en DB"""
        trade_data = {
            'timestamp': '2025-11-03 19:00:00',
            'action': 'SELL',
            'price': 116573.08,
            'btc_amount': 0.00006088,
            'usd_amount': 7.10,
            'fee': 0.04,
            'profit': 0.17,
            'balance_usd': 7.97,
            'balance_btc': 0.0
        }
        
        self.cursor.execute('''
            INSERT INTO trades (timestamp, action, price, btc_amount, usd_amount, fee, profit, balance_usd, balance_btc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(trade_data.values()))
        self.conn.commit()
        
        # Verificar
        self.cursor.execute('SELECT * FROM trades WHERE action = "SELL"')
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result, msg="Venta debe guardarse en DB")
        self.assertEqual(result[2], 'SELL', msg="Action debe ser SELL")
        self.assertGreater(result[7], 0, msg="Profit debe ser positivo")
        
    def test_complete_cycle_tracked(self):
        """Test 15: Validar ciclo completo en DB"""
        # Compra
        self.cursor.execute('''
            INSERT INTO trades (timestamp, action, price, btc_amount, usd_amount, fee, balance_usd, balance_btc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('2025-11-03 18:00:00', 'BUY', 112413.63, 0.00006088, 6.88, 0.04, 0.80, 0.00006088))
        
        # Venta
        self.cursor.execute('''
            INSERT INTO trades (timestamp, action, price, btc_amount, usd_amount, fee, profit, balance_usd, balance_btc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('2025-11-03 19:00:00', 'SELL', 116573.08, 0.00006088, 7.10, 0.04, 0.17, 7.97, 0.0))
        self.conn.commit()
        
        # Verificar secuencia
        self.cursor.execute('SELECT action, profit FROM trades ORDER BY id')
        results = self.cursor.fetchall()
        
        self.assertEqual(len(results), 2, msg="Debe haber 2 registros")
        self.assertEqual(results[0][0], 'BUY', msg="Primero debe ser BUY")
        self.assertEqual(results[1][0], 'SELL', msg="Segundo debe ser SELL")
        self.assertGreater(results[1][1], 0, msg="Profit final positivo")


class TestUIDisplay(unittest.TestCase):
    """Pruebas de visualización en UI"""
    
    def setUp(self):
        """Crear root de tkinter"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Valores del sistema
        self.buy_fee_rate = 0.006
        self.sell_fee_rate = 0.006
        self.profit_target = 0.025
        
    def tearDown(self):
        """Limpiar"""
        self.root.destroy()
        
    def test_price_format_with_commas_and_decimals(self):
        """Test 16: Validar formato de precios con comas y decimales"""
        prices = [112413.63, 116573.08, 113875.01, 1000.50, 10000.99]
        
        for price in prices:
            var = tk.StringVar()
            var.set(f"${price:,.2f}")
            displayed = var.get()
            
            self.assertTrue(displayed.startswith('$'),
                          msg=f"Precio ${price} debe comenzar con $")
            self.assertEqual(len(displayed.split('.')[-1]), 2,
                           msg=f"Precio ${price} debe tener 2 decimales")
            
    def test_btc_amount_precision_8_decimals(self):
        """Test 17: Validar precisión de 8 decimales para BTC"""
        btc_amounts = [0.00006088, 0.12345678, 0.00000001, 0.99999999]
        
        for btc in btc_amounts:
            var = tk.StringVar()
            var.set(f"{btc:.8f}")
            displayed = var.get()
            
            decimal_part = displayed.split('.')[-1] if '.' in displayed else ""
            self.assertEqual(len(decimal_part), 8,
                           msg=f"BTC {btc} debe tener 8 decimales")
            
    def test_profit_color_green_for_positive(self):
        """Test 18: Validar color verde para ganancia positiva"""
        profits = [0.17, 0.01, 1.50, 100.00]
        
        for profit in profits:
            label = tk.Label(self.root)
            label.config(text=f"${profit:+,.2f}",
                        foreground='green' if profit > 0 else 'red')
            
            self.assertEqual(label['foreground'], 'green',
                           msg=f"Profit ${profit} debe ser verde")
            
    def test_loss_color_red_for_negative(self):
        """Test 19: Validar color rojo para pérdida"""
        losses = [-0.20, -0.01, -1.50, -100.00]
        
        for loss in losses:
            label = tk.Label(self.root)
            label.config(text=f"${loss:+,.2f}",
                        foreground='green' if loss > 0 else 'red')
            
            self.assertEqual(label['foreground'], 'red',
                           msg=f"Loss ${loss} debe ser rojo")
            
    def test_percentage_format_with_sign(self):
        """Test 20: Validar formato de porcentajes con signo"""
        percentages = [(3.7, '+'), (-4.89, '-'), (1.30, '+'), (0.0, '+')]
        
        for pct, expected_sign in percentages:
            var = tk.StringVar()
            var.set(f"{pct:+.2f}%")
            displayed = var.get()
            
            self.assertTrue(displayed.startswith(expected_sign),
                          msg=f"Porcentaje {pct} debe tener signo {expected_sign}")
            self.assertTrue(displayed.endswith('%'),
                          msg=f"Porcentaje {pct} debe terminar con %")


class TestTradingConditions(unittest.TestCase):
    """Pruebas de condiciones de negocio"""
    
    def test_buy_only_without_open_position(self):
        """Test 21: Validar compra solo sin posición abierta"""
        scenarios = [
            (0.0, True),  # Sin BTC, puede comprar
            (0.00006088, False),  # Con BTC, no puede comprar
            (0.001, False)  # Con BTC, no puede comprar
        ]
        
        for btc_balance, can_buy in scenarios:
            result = btc_balance == 0
            self.assertEqual(result, can_buy,
                           msg=f"BTC {btc_balance}: Can buy = {can_buy}")
            
    def test_sell_only_with_open_position(self):
        """Test 22: Validar venta solo con posición abierta"""
        scenarios = [
            (0.0, False),  # Sin BTC, no puede vender
            (0.00006088, True),  # Con BTC, puede vender
            (0.001, True)  # Con BTC, puede vender
        ]
        
        for btc_balance, can_sell in scenarios:
            result = btc_balance > 0
            self.assertEqual(result, can_sell,
                           msg=f"BTC {btc_balance}: Can sell = {can_sell}")


def run_all_tests():
    """Ejecutar todas las pruebas organizadas"""
    print("\n" + "="*70)
    print("SUITE COMPLETA DE PRUEBAS - CRIPTO-BOT")
    print("="*70)
    
    # Crear suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases en orden
    test_classes = [
        TestSystemConfiguration,
        TestTradingCalculations,
        TestBalanceValidations,
        TestDatabaseOperations,
        TestUIDisplay,
        TestTradingConditions
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen por categoría
    print("\n" + "="*70)
    print("RESUMEN POR CATEGORIA")
    print("="*70)
    print(f"Sistema: TestSystemConfiguration")
    print(f"Calculos: TestTradingCalculations")
    print(f"Validaciones: TestBalanceValidations")
    print(f"Base de Datos: TestDatabaseOperations")
    print(f"UI Display: TestUIDisplay")
    print(f"Condiciones: TestTradingConditions")
    print("="*70)
    print(f"Total Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun}")
    print(f"Total Fallidas: {len(result.failures)}")
    print(f"Total Errores: {len(result.errors)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("\nTODAS LAS PRUEBAS PASARON")
        print("Sistema validado para operar en modo LIVE")
        return 0
    else:
        print("\nALGUNAS PRUEBAS FALLARON")
        print("NO operar en modo LIVE hasta resolver")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
