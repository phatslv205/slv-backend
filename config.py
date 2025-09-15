# config.py

import os
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()

# Cấu hình chính
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY") or "slv-secret-key"

# Danh sách key OpenAI (ngoài class để dễ import)
OPENAI_KEYS = [
    k.strip() for k in os.getenv("OPENAI_KEYS", "").split(",")
    if k.strip().startswith("sk-")
]

# In thông tin
print("📦 Tổng số key đọc được:", len(OPENAI_KEYS))
if OPENAI_KEYS:
    print("📦 Key đầu tiên:", OPENAI_KEYS[0])
else:
    print("❌ Không có key nào trong biến môi trường OPENAI_KEYS")
