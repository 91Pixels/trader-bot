"""
Set TRADING_MODE to LIVE for real balance
"""
from pathlib import Path

env_file = Path(__file__).parent / '.env'

print("="*70)
print("SETTING LIVE MODE FOR REAL BALANCE")
print("="*70)
print()

# Read current .env
with open(env_file, 'r') as f:
    lines = f.readlines()

# Update TRADING_MODE to LIVE
new_lines = []
found = False

for line in lines:
    if line.startswith('TRADING_MODE='):
        new_lines.append('TRADING_MODE=LIVE\n')
        found = True
        print("✅ Changed: TRADING_MODE=SIMULATION → TRADING_MODE=LIVE")
    else:
        new_lines.append(line)

if not found:
    new_lines.append('\nTRADING_MODE=LIVE\n')
    print("✅ Added: TRADING_MODE=LIVE")

# Write back
with open(env_file, 'w') as f:
    f.writelines(new_lines)

print()
print("="*70)
print("✅ LIVE MODE ACTIVATED")
print("="*70)
print()
print("Ahora tu GUI mostrará:")
print("  ✅ Balance real de Coinbase")
print("  ✅ Account (Real Balance from Coinbase)")
print("  ✅ USD: $0.00")
print("  ✅ BTC: 0.00004323")
print()
print("Para aplicar los cambios:")
print("  1. Cierra la ventana de la GUI actual")
print("  2. Ejecuta: python btc_trader.py")
print()
print("="*70)
