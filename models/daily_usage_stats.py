import uuid
from extensions import db
from datetime import date
from models import User  # Import đúng theo dự án bạn
from datetime import datetime
class DailyUsageStats(db.Model):
    __tablename__ = "daily_usage_stats"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, default=date.today, unique=True)

    slv_count = db.Column(db.Integer, default=0)      # Lượt GPT chính (SLV)
    lite_count = db.Column(db.Integer, default=0)     # Lượt AI Lite

    total_users = db.Column(db.Integer, default=0)
    online_users = db.Column(db.Integer, default=0)
    gpt_users = db.Column(db.Integer, default=0)
    blocked_users = db.Column(db.Integer, default=0)
    over_100_gpt = db.Column(db.Integer, default=0)

# Gọi mỗi khi user dùng AI (đã có sẵn)
def update_daily_usage(is_slv=True):
    today = date.today()
    stats = DailyUsageStats.query.filter_by(date=today).first()
    if not stats:
        stats = DailyUsageStats(date=today)
        db.session.add(stats)

    if is_slv:
        stats.slv_count = (stats.slv_count or 0) + 1
        print("✅ Đã ghi nhận 1 lượt SLV")
    else:
        stats.lite_count = (stats.lite_count or 0) + 1
        print("✅ Đã ghi nhận 1 lượt Lite")

    db.session.commit()

# Gọi 1 lần lúc 23h59 mỗi ngày
def finalize_daily_stats(app):
    with app.app_context():
        today = date.today()
        stats = DailyUsageStats.query.filter_by(date=today).first()

        if not stats:
            stats = DailyUsageStats(date=today)

        stats.total_users = User.query.count()
        stats.online_users = User.query.filter_by(online=True).count()
        stats.gpt_users = User.query.filter(
            User.vip_gpt_ai.is_(True),
            User.vip_until_gpt > datetime.utcnow()
        ).count()
        stats.blocked_users = User.query.filter_by(chat_blocked_due_to_quota=True).count()
        stats.over_100_gpt = User.query.filter(User.gpt_usage_today > 100).count()

        if not stats.id:
            db.session.add(stats)

        db.session.commit()
        print(f"✅ [DAILY] Đã lưu thống kê ngày {today}")
