import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from totp.totp_utils import generate_totp_code, verify_totp_code


# Example 64-char hex seed (random bytes shown as hex). Replace with your seed.
hex_seed = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

code = generate_totp_code(hex_seed)
print("Generated code:", code)

ok = verify_totp_code(hex_seed, code)   # should be True
print("Verify (should be True):", ok)
