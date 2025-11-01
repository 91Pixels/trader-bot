# Unit Tests Documentation

Complete test suite for the BTC Trading Bot project.

## Test Structure

```
tests/
├── __init__.py                 # Package initialization
├── test_calculations.py        # Trading calculations tests
├── test_coinbase_api.py        # API integration tests
├── test_trading_logic.py       # Trading logic tests
├── run_all_tests.py           # Test runner
└── README.md                   # This file
```

## Test Suites

### 1. `test_calculations.py`
Tests all trading calculation formulas to ensure accuracy:

- ✅ BTC quantity calculation after buy fee
- ✅ Target price formula (correct implementation)
- ✅ Net profit verification ($1.50 on $100 position)
- ✅ Fee calculations (buy + sell)
- ✅ Stop loss price calculation
- ✅ Profit percentage from target
- ✅ Different position sizes
- ✅ Edge cases and boundary conditions
- ✅ Unrealized P/L calculation

**Total Tests:** 10

### 2. `test_coinbase_api.py`
Tests Coinbase API connectivity and error handling:

- ✅ API connectivity
- ✅ Response format validation
- ✅ Price data validation
- ✅ Timeout handling
- ✅ Error response handling
- ✅ Invalid JSON handling
- ✅ Missing field handling
- ✅ Multiple requests consistency
- ✅ Rate limiting behavior

**Total Tests:** 12

### 3. `test_trading_logic.py`
Tests trading logic including auto buy/sell:

- ✅ Auto buy trigger conditions
- ✅ Auto buy single execution
- ✅ Auto buy with existing position
- ✅ Auto buy enable/disable
- ✅ Trigger price calculation
- ✅ Sell at target price
- ✅ Sell at stop loss
- ✅ Manual vs auto mode
- ✅ Balance validation
- ✅ Position tracking

**Total Tests:** 20+

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test Suite
```bash
# Calculations only
pytest tests/test_calculations.py -v

# API tests only
pytest tests/test_coinbase_api.py -v

# Trading logic only
pytest tests/test_trading_logic.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Run Specific Test
```bash
pytest tests/test_calculations.py::TestTradingCalculations::test_target_price_formula -v
```

## Test Coverage Goals

- **Calculations:** 100% coverage
- **API Integration:** 90%+ coverage
- **Trading Logic:** 95%+ coverage
- **Overall Project:** 85%+ coverage

## Continuous Integration

Tests are automatically run in Jenkins pipeline before any deployment:

1. **Code Quality Checks** (pylint, flake8)
2. **Unit Tests** (all suites)
3. **Coverage Report** (minimum 85%)
4. **Security Scan** (safety, bandit)

See `Jenkinsfile` in project root for CI/CD configuration.

## Adding New Tests

### Template for New Test
```python
import unittest

class TestNewFeature(unittest.TestCase):
    """Test description"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_feature(self):
        """Test specific behavior"""
        # Arrange
        expected = 100
        
        # Act
        result = some_function()
        
        # Assert
        self.assertEqual(result, expected)
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (test_should_do_x_when_y)
3. **AAA pattern** (Arrange, Act, Assert)
4. **Mock external dependencies** (API calls, file I/O)
5. **Test edge cases** (zero, negative, very large values)
6. **Test error conditions** (invalid input, exceptions)

## Critical Test Cases

### ⚠️ MUST PASS Before Deployment

1. **Net Profit Accuracy**
   - `test_net_profit_at_target` - Verifies $1.50 profit on $100

2. **Target Price Formula**
   - `test_target_price_formula` - Correct formula implementation

3. **API Connectivity**
   - `test_api_connectivity` - Can connect to Coinbase

4. **Auto Buy Logic**
   - `test_auto_buy_trigger_condition` - Triggers at correct price

5. **Auto Sell Logic**
   - `test_sell_at_target` - Sells at target price

## Test Results Interpretation

### Success Output
```
======================================================================
TEST SUMMARY
======================================================================
Tests run: 42
Successes: 42
Failures: 0
Errors: 0
Skipped: 0
======================================================================
```

### Failure Output
```
FAILED tests/test_calculations.py::test_target_price_formula
AssertionError: 35945.0 != 36000.0
```

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'requests'`
- **Solution:** `pip install -r requirements.txt`

**Issue:** API tests failing with timeout
- **Solution:** Check internet connection, Coinbase API may be down

**Issue:** Import errors in tests
- **Solution:** Ensure `sys.path.insert` is correctly pointing to parent directory

## Maintenance

- **Review tests** when adding new features
- **Update tests** when changing calculations
- **Add tests** for bug fixes to prevent regression
- **Run tests locally** before committing code
- **Check CI/CD pipeline** after pushing changes

## Contact

For questions about tests, refer to the main `README.md` or review the Jenkins pipeline logs.
