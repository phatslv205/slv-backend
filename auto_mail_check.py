import os
import imaplib
import email
import re
from datetime import datetime
from extensions import db
from models import User, Transaction
from run import grant_vip

def parse_email_content(content):
    # Sử dụng định dạng mới: tkthiham123 goiSLV(5day) maTXN_E5KX28
    match = re.search(r'tk(\w+)\s+goiSLV\((\d+day)\)\s+ma(\w+)', content, re.IGNORECASE)
    if match:
        username = match.group(1).strip()
        duration = match.group(2).strip()  # 5day / 15day / 30day
        txn_code = match.group(3).strip()
        pkg_code = f"SLV({duration})"
        return username, pkg_code, txn_code
    elif "lite" in content.lower():
        match2 = re.search(r'tk(\w+)\s+goiLITE\s+ma(\w+)', content, re.IGNORECASE)
        if match2:
            username = match2.group(1).strip()
            txn_code = match2.group(2).strip()
            return username, "vip_ai_lite", txn_code
    return None, None, None

def auto_approve_transactions():
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("⚠️ Chưa có EMAIL_ADDRESS hoặc EMAIL_PASSWORD trong .env")
        return

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, "UNSEEN")
        mail_ids = data[0].split()

        for num in mail_ids:
            result, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg["subject"] or ""
            content = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        content += part.get_payload(decode=True).decode()
            else:
                content = msg.get_payload(decode=True).decode()

            full_text = subject + "\n" + content
            username, pkg_code, txn_code = parse_email_content(full_text)

            if not username or not pkg_code or not txn_code:
                print("⚠️ Không tìm thấy nội dung hợp lệ trong mail.")
                continue

            print(f"✅ Tìm thấy giao dịch: {username} - {pkg_code} - {txn_code}")

            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"❌ Không tìm thấy user: {username}")
                continue

            existing = Transaction.query.filter_by(txn_code=txn_code).first()
            if existing:
                print(f"⚠️ Mã giao dịch {txn_code} đã được xử lý.")
                continue

            # Lưu vào bảng transaction
            txn = Transaction(
                user_id=user.user_id,
                txn_code=txn_code,
                method="visa_email",
                package=pkg_code,
                status="approved",
                created_at=datetime.utcnow()
            )
            db.session.add(txn)

            # Ánh xạ tên gói
            pkg_map = {
                "vip_ai_lite": "vip_ai_lite",
                "SLV(5day)": "vip_gpt_5d",
                "SLV(15day)": "vip_gpt_15d",
                "SLV(30day)": "vip_gpt_30d"
            }
            selected_pkg = pkg_map.get(pkg_code)
            if not selected_pkg:
                print(f"❌ Gói không hợp lệ: {pkg_code}")
                continue

            result = grant_vip(username, selected_pkg)
            print("🎁 Kết quả cấp gói:", result)

            db.session.commit()

        mail.logout()

    except Exception as e:
        print("❌ Lỗi khi quét mail:", e)
