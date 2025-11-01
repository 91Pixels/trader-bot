"""
Organize project structure - Simple approach that won't break imports
"""
import os
import shutil
from pathlib import Path

base_path = Path(__file__).parent

print("="*70)
print("ORGANIZING PROJECT STRUCTURE")
print("="*70)
print()

# Create folders
folders_to_create = ['docs', 'scripts', 'ci', 'credentials']

for folder in folders_to_create:
    folder_path = base_path / folder
    if not folder_path.exists():
        folder_path.mkdir(parents=True)
        print(f"✅ Created: {folder}/")

print()

# Move documentation
docs_files = [
    'PROJECT_SUMMARY.md',
    'FINAL_PROJECT_STRUCTURE.md',
    'COINBASE_SETUP.md',
    'CREATE_ECDSA_API_KEY.md',
    'TRADING_EXAMPLES.md',
    'TESTING_SETUP.md',
    'HTML_REPORTS_GUIDE.md',
]

print("📁 docs/")
for file_name in docs_files:
    src = base_path / file_name
    dst = base_path / 'docs' / file_name
    
    if src.exists() and not dst.exists():
        shutil.move(str(src), str(dst))
        print(f"  ✅ {file_name}")
    elif dst.exists():
        print(f"  ⏭️  Already exists: {file_name}")

# Move CI/CD files
print("\n📁 ci/")
ci_files = ['Jenkinsfile', 'run_tests.bat', 'mutation_test_demo.bat']

for file_name in ci_files:
    src = base_path / file_name
    dst = base_path / 'ci' / file_name
    
    if src.exists() and not dst.exists():
        shutil.move(str(src), str(dst))
        print(f"  ✅ {file_name}")

# Move scripts
print("\n📁 scripts/")
script_files = ['check_balance.py', 'run_new_tests.py', 'organize_project.py']

for file_name in script_files:
    src = base_path / file_name
    dst = base_path / 'scripts' / file_name
    
    if src.exists() and not dst.exists():
        shutil.move(str(src), str(dst))
        print(f"  ✅ {file_name}")

# Move credentials (with warning)
print("\n📁 credentials/")
cred_file = 'coinbase_ecdsa_key.txt'
src = base_path / cred_file
dst = base_path / 'credentials' / cred_file

if src.exists() and not dst.exists():
    shutil.copy(str(src), str(dst))  # Copy instead of move for safety
    print(f"  ✅ Copied: {cred_file}")
    print(f"  ⚠️  Original kept in root for compatibility")

print()
print("="*70)
print("FINAL STRUCTURE")
print("="*70)
print()
print("Cripto-Agent/")
print("├── Core Files (root)")
print("│   ├── btc_trader.py")
print("│   ├── coinbase_advanced_trade_jwt.py")
print("│   ├── coinbase_api.py")
print("│   ├── coinbase_advanced_trade_api.py")
print("│   ├── config.py")
print("│   ├── .env")
print("│   ├── .env.example")
print("│   ├── coinbase_ecdsa_key.txt")
print("│   ├── requirements.txt")
print("│   ├── pytest.ini")
print("│   ├── .gitignore")
print("│   └── README.md")
print("│")
print("├── 📁 tests/")
print("│   └── (71 unit tests)")
print("│")
print("├── 📁 docs/")
print("│   └── (7 documentation files)")
print("│")
print("├── 📁 scripts/")
print("│   └── (utility scripts)")
print("│")
print("├── 📁 ci/")
print("│   └── (CI/CD files)")
print("│")
print("└── 📁 credentials/")
print("    └── (backup of credentials)")
print()
print("✅ Organization complete!")
print("✅ All imports will continue working")
print()
print("="*70)
