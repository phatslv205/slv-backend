import smtplib
from email.message import EmailMessage

EMAIL = "phatth.viettel@gmail.com"      # ⚠️ Đổi thành email thật của bạn
PASS = "wbmzxjtfcvlgfoag"          # ⚠️ Không dùng mật khẩu Gmail thường, mà dùng App Password

msg = EmailMessage()
msg["Subject"] = "Chuyen tien"
msg["From"] = EMAIL
msg["To"] = EMAIL
msg.set_content("Da chuyen 250000 VNĐ\nMa giao dich: TXN9772355032053760")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL, PASS)
    smtp.send_message(msg)
