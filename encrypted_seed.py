from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# Replace this with your actual 64-character hex seed
hex_seed = "a0cad79507e3b29bb6ad4b6f2fae762f21237a5a672b97ed5389e4e1c2a18b2a"

# Load public key
with open("data/student_public.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

# Convert hex string to bytes
seed_bytes = hex_seed.encode("utf-8")

# Encrypt using RSA-OAEP with SHA-256
ciphertext = public_key.encrypt(
    seed_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Encode to base64 string
encrypted_base64 = base64.b64encode(ciphertext).decode()

print("🔐 Encrypted Seed (base64):")
print(encrypted_base64)
