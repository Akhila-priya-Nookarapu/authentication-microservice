import base64
import re
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed(encrypted_seed_b64: str, private_key):
    # 1. Decode base64
    ciphertext = base64.b64decode(encrypted_seed_b64)

    # 2. Decrypt using RSA-OAEP SHA256
    plaintext_bytes = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3. Convert to string
    seed = plaintext_bytes.decode("utf-8").strip()

    # 4. Validate seed is 64-char hex
    if not re.fullmatch(r"[0-9a-f]{64}", seed):
        raise ValueError("Invalid decrypted seed")

    # 5. Save to file
    with open("data/seed.txt", "w") as f:
        f.write(seed + "\n")

    return seed
