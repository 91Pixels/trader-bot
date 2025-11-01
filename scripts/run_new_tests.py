"""
Run all new unit tests for the working implementation
"""
import subprocess
import sys

print("="*70)
print("RUNNING UNIT TESTS")
print("="*70)
print()

# Run pytest with coverage
result = subprocess.run([
    sys.executable, '-m', 'pytest',
    'tests/test_coinbase_jwt_api.py',
    'tests/test_config.py',
    'tests/test_balance_check.py',
    '-v',
    '--tb=short',
    '--color=yes'
], cwd='.')

print()
print("="*70)

if result.returncode == 0:
    print("✅ ALL TESTS PASSED")
else:
    print("❌ SOME TESTS FAILED")

print("="*70)

sys.exit(result.returncode)
