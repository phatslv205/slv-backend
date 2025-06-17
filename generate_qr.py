import pyotp
import qrcode

secret = "CPNCQT5XYA3GLINBRCZTSSKDQSORLQDU"  # ← đây là secret đang dùng trong Flask
totp = pyotp.TOTP(secret)

uri = totp.provisioning_uri(name="admin@slv", issuer_name="SLV Admin")
qrcode.make(uri).save("admin_fixed_qr.png")
print("✅ Đã tạo lại QR chính xác.")
