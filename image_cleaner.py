import os
import time

UPLOAD_FOLDER = "static/images/uploads"
EXPIRY_DAYS = 7  # 🗓️ 7 ngày

def clean_old_images():
    now = time.time()
    expiry_seconds = EXPIRY_DAYS * 86400  # 7 ngày = 604800 giây
    deleted = 0

    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for filename in files:
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                path = os.path.join(root, filename)
                try:
                    modified_time = os.path.getmtime(path)
                    if now - modified_time > expiry_seconds:
                        os.remove(path)
                        print(f"🗑️ Đã xoá: {path}")
                        deleted += 1
                except Exception as e:
                    print(f"❌ Lỗi xoá {path}: {e}")

    if deleted > 0:
        print(f"✅ Đã xoá {deleted} ảnh cũ hơn {EXPIRY_DAYS} ngày.")
    return deleted
