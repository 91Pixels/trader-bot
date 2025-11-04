from config import Config
from coinbase import jwt_generator

print("="*60)
print("JWT TEST")
print("="*60)

try:
    # Test JWT generation
    test_uri = "GET /api/v3/brokerage/accounts"
    token = jwt_generator.build_rest_jwt(
        test_uri,
        Config.COINBASE_API_KEY,
        Config.COINBASE_API_SECRET
    )
    print(f"✅ JWT Token generated successfully")
    print(f"Token (first 50 chars): {token[:50]}...")
except Exception as e:
    print(f"❌ Error generating JWT: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
