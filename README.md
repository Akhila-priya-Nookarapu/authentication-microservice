# **PKI + TOTP Authentication Microservice**

A secure, containerized authentication microservice implementing **RSA 4096-bit PKI**, **TOTP-based 2FA**, **FastAPI**, **Docker**, and **cron automation**.

---

## **📌 Project Overview**

This microservice demonstrates enterprise-grade security practices using:

* **Public Key Infrastructure (PKI)**
* **RSA 4096-bit encryption & signatures**
* **TOTP-based Two-Factor Authentication**
* **REST API development (FastAPI)**
* **Containerization using Docker**
* **Automated cron jobs**
* **Persistent storage volumes**

This system securely decrypts a seed, generates TOTP codes, verifies user codes, and logs codes automatically every minute inside a Docker container.

---

## **✨ Features**

### 🔐 **Cryptography**

* RSA **4096-bit** key pair
* RSA-OAEP SHA-256 decryption
* RSA-PSS SHA-256 signature generation
* Signature encryption using instructor public key

### 🔑 **API Endpoints**

| Endpoint        | Method | Description                                      |
| --------------- | ------ | ------------------------------------------------ |
| `/decrypt-seed` | POST   | Decrypt encrypted seed using student private key |
| `/generate-2fa` | GET    | Generate current TOTP code + seconds remaining   |
| `/verify-2fa`   | POST   | Validate a submitted 6-digit TOTP code           |

### ⏱️ **TOTP Parameters**

* SHA-1
* 30-second window
* 6-digit codes
* Base32 conversion of 64-char hex seed
* ±1 window tolerance for verification

### 🐳 **Dockerized Microservice**

* Multi-stage Dockerfile
* UTC timezone enforced
* Cron daemon installed & running
* `/data` and `/cron` persistent volumes
* API available on port **8080**

### 🕒 **Cron Job**

Runs **every minute**:

* Reads seed
* Generates TOTP code
* Logs timestamp + code to:

  ```
  /cron/last_code.txt
  ```

---

## **📂 Project Structure**

```
pki-totp-microservice/
│
├── app/
│   ├── main.py
│   ├── crypto_utils.py
│   └── __init__.py
│
├── scripts/
│   ├── request_seed.py
│   ├── log_2fa_cron.py
│   └── sign_commit.py
│
├── cron/
│   └── 2fa-cron
│
├── student_private.pem
├── student_public.pem
├── instructor_public.pem
│
├── encrypted_seed.txt
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## **🚀 Running the Service**

### **1️⃣ Build**

```
docker compose build
```

### **2️⃣ Start**

```
docker compose up -d
```

### **3️⃣ Test Endpoints**

#### **Decrypt Seed**

```
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"
```

#### **Generate TOTP Code**

```
curl http://localhost:8080/generate-2fa
```

#### **Verify TOTP Code**

```
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"123456\"}"
```

---

## **🕒 Cron Output Verification**

Check logged TOTP codes:

```
docker exec pki-totp-app cat /cron/last_code.txt
```

Example output:

```
2025-12-05 14:24:01 2FA Code: 776214
2025-12-05 14:25:01 2FA Code: 753857
2025-12-05 14:26:01 2FA Code: 042981
```

---

## **🧪 Commit Proof Generation**

Run:

```
python scripts/sign_commit.py
```

Outputs:

* **Commit Hash**
* **Encrypted Commit Signature (Base64)**

These are submitted to the instructor portal.

---

## **📦 Technologies Used**

* Python 3.10+
* FastAPI
* Cryptography library
* PyOTP
* Docker + Docker Compose
* Cron (Linux)
* RSA-4096, OAEP, PSS

---

## **✔️ Assignment Requirements — All Completed**

This project meets all required criteria:

* ✔️ RSA-4096 Key Pair
* ✔️ OAEP-SHA256 Decryption
* ✔️ PSS-SHA256 Signing
* ✔️ Encrypted Signature Output
* ✔️ TOTP Generation & Verification
* ✔️ FastAPI Microservice
* ✔️ Docker Multi-Stage Build
* ✔️ Cron Job Logging Every Minute
* ✔️ Persistent Volumes
* ✔️ UTC Timezone
* ✔️ Working API Endpoints
* ✔️ Commit Proof Script

---

