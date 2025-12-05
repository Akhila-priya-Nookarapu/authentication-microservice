from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64, os, time

from totp.totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load private key ONCE
with open("data/student_private.pem", "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

# ---- Decrypt Seed ----

class DecryptRequest(BaseModel):
    encrypted_seed: str

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(req: DecryptRequest):
    try:
        # 1. Base64 decode
        cipher_bytes = base64.b64decode(req.encrypted_seed)

        # 2. RSA decrypt (OAEP with SHA256)
        plaintext = PRIVATE_KEY.decrypt(
            cipher_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 3. Convert to string
        seed = plaintext.decode("utf-8").strip()

        # 4. Validate 64-char hex
        if len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed.lower()):
            return JSONResponse(status_code=400, content={"error": "Invalid seed format"})

        # 5. Save
        with open("data/seed.txt", "w") as f:
            f.write(seed + "\n")

        return {"seed": seed}

    except Exception as e:
        print("Decrypt Error:", e)
        return JSONResponse(status_code=500, content={"error": "Decryption failed"})


# ---- Generate TOTP ----

@app.get("/generate-2fa")
async def generate_2fa():
    try:
        with open("data/seed.txt", "r") as f:
            seed = f.read().strip()
    except:
        return JSONResponse(status_code=500, content={"error": "Seed not decrypted yet"})

    code = generate_totp_code(seed)
    now = int(time.time())
    valid_for = 30 - (now % 30)
    return {"code": code, "valid_for": valid_for}


# ---- Verify TOTP ----

@app.post("/verify-2fa")
async def verify_2fa(payload: dict = Body(...)):
    try:
        code = payload.get("code")
        if not code:
            return JSONResponse(status_code=400, content={"error": "Missing code"})

        with open("data/seed.txt", "r") as f:
            seed = f.read().strip()

        valid = verify_totp_code(seed, code, valid_window=1)
        return {"valid": valid}

    except Exception as e:
        print("Verify Error:", e)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
