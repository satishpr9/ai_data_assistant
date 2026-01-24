from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prepare_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def hash_password(password: str) -> str:
    prepared = _prepare_password(password)
    return pwd_context.hash(prepared)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    prepared = _prepare_password(plain_password)
    return pwd_context.verify(prepared, hashed_password)

# Test with long password
print("Testing long password...")
long_pw = "a" * 100
print(f"Length: {len(long_pw.encode('utf-8'))} bytes")

try:
    hashed = hash_password(long_pw)
    assert verify_password(long_pw, hashed)
    print("✅ SUCCESS - No error!")
except Exception as e:
    print(f"❌ FAILED: {e}")