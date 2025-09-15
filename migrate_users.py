import json
from run import app
from extensions import db
from models.user import User

with open("users.json", "r", encoding="utf-8") as f:
    users = json.load(f)

with app.app_context():
    count = 0
    for username, info in users.items():
        password = info.get("password", "")
        fullname = info.get("fullname", "")
        bio = info.get("bio", "")
        birthday = info.get("birthday", "")
        # VIP xử lý linh hoạt hơn
        vip_raw = str(info.get("vip_gpt", "")).lower()
        vip_gpt = vip_raw in ["1", "true", "yes", "5day", "vip"]

        user = User(
            user_id = info.get("user_id"),  # nếu bạn dùng cột UUID làm ID
            username=username,
            password=password,
            email=info.get("email", ""),
            fullname=info.get("fullname", ""),
            bio=info.get("bio", ""),
            birthday=info.get("birthday", ""),
            verified=bool(info.get("verified", False)),
            otp_code=info.get("otp_code", ""),
            online=bool(info.get("online", False)),
            vip_gpt=vip_gpt,
            # các trường khác tuỳ bạn mở rộng model
        )

        db.session.add(user)
        count += 1

    db.session.commit()
    print(f"✅ Đã chuyển {count} user từ JSON vào PostgreSQL.")
