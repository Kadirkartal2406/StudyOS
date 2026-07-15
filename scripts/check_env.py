#!/usr/bin/env python3
"""
StudyOS — Ortam Değişkeni Doğrulama Betiği
Kullanım: python scripts/check_env.py
"""
import os
import sys

REQUIRED_VARS = [
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_S3_BUCKET_NAME",
]

OPTIONAL_VARS = [
    "GEMINI_API_KEY",
    "FIREBASE_PROJECT_ID",
    "SMTP_USERNAME",
    "SENTRY_DSN",
]


def check_env() -> bool:
    print("StudyOS Ortam Değişkeni Kontrolü")
    print("=" * 40)

    all_ok = True

    print("\n[Zorunlu]")
    for var in REQUIRED_VARS:
        val = os.getenv(var)
        if val and val not in ("change-me-use-openssl-rand-hex-32", "change-me-in-production"):
            print(f"  ✓ {var}")
        else:
            print(f"  ✗ {var} — EKSİK VEYA VARSAYILAN DEĞER")
            all_ok = False

    print("\n[Opsiyonel]")
    for var in OPTIONAL_VARS:
        val = os.getenv(var)
        status = "✓" if val else "○ (boş)"
        print(f"  {status} {var}")

    print("\n" + "=" * 40)
    if all_ok:
        print("✅ Tüm zorunlu değişkenler tanımlı.")
    else:
        print("❌ Eksik değişkenler var. .env dosyasını kontrol edin.")

    return all_ok


if __name__ == "__main__":
    # .env dosyasını yükle (varsa)
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    ok = check_env()
    sys.exit(0 if ok else 1)
