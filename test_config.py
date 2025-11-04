from config import Config

print("="*60)
print("CONFIG TEST")
print("="*60)
print(f"API Key: {Config.COINBASE_API_KEY[:30] if Config.COINBASE_API_KEY else 'Not Set'}...")
print(f"API Secret starts with: {Config.COINBASE_API_SECRET[:30] if Config.COINBASE_API_SECRET else 'Not Set'}...")
print(f"Private Key File: {Config.PRIVATE_KEY_FILE}")
print(f"Trading Mode: {Config.TRADING_MODE}")
print("="*60)
