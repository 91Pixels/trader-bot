"""
Organize project structure into proper folders
"""
import os
import shutil
from pathlib import Path

base_path = Path(__file__).parent

# Define folder structure
STRUCTURE = {
    'src': [
        'btc_trader.py',
        'coinbase_advanced_trade_jwt.py',
        'coinbase_api.py',
        'coinbase_advanced_trade_api.py',
        'config.py',
    ],
    'scripts': [
        'check_balance.py',
        'run_new_tests.py',
    ],
    'docs': [
        'README.md',
        'PROJECT_SUMMARY.md',
        'FINAL_PROJECT_STRUCTURE.md',
        'COINBASE_SETUP.md',
        'CREATE_ECDSA_API_KEY.md',
        'TRADING_EXAMPLES.md',
        'TESTING_SETUP.md',
        'HTML_REPORTS_GUIDE.md',
    ],
    'config': [
        '.env.example',
        'pytest.ini',
        'requirements.txt',
    ],
    'ci': [
        'Jenkinsfile',
        'run_tests.bat',
        'mutation_test_demo.bat',
    ],
    'credentials': [
        'coinbase_ecdsa_key.txt',
    ],
}

print("="*70)
print("ORGANIZING PROJECT STRUCTURE")
print("="*70)
print()

# Create folders
for folder in STRUCTURE.keys():
    folder_path = base_path / folder
    if not folder_path.exists():
        folder_path.mkdir(parents=True)
        print(f"✅ Created folder: {folder}/")

print()

# Move files
moved_count = 0
skipped_count = 0

for folder, files in STRUCTURE.items():
    print(f"\n📁 {folder}/")
    for file_name in files:
        src = base_path / file_name
        dst = base_path / folder / file_name
        
        if src.exists() and not dst.exists():
            try:
                shutil.move(str(src), str(dst))
                print(f"  ✅ Moved: {file_name}")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Failed: {file_name} - {e}")
                skipped_count += 1
        elif dst.exists():
            print(f"  ⏭️  Already in place: {file_name}")
            skipped_count += 1
        else:
            print(f"  ⏭️  Not found: {file_name}")
            skipped_count += 1

print()
print("="*70)
print("SUMMARY")
print("="*70)
print(f"✅ Moved: {moved_count} files")
print(f"⏭️  Skipped: {skipped_count} files")
print()

# Create __init__.py in src
src_init = base_path / 'src' / '__init__.py'
if not src_init.exists():
    src_init.write_text('"""Source code for BTC Trading Bot"""')
    print("✅ Created: src/__init__.py")

# Update imports info
print()
print("⚠️  IMPORTANT: You need to update imports in files!")
print()
print("Next steps:")
print("1. Update imports in test files to use 'src.' prefix")
print("2. Add 'src' to Python path")
print("3. Run tests to verify")
print()
print("="*70)
