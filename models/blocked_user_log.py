# blocked_user_log.py

from extensions import db
from datetime import datetime
from pytz import timezone

# ✅ Múi giờ Việt Nam
vn_tz = timezone("Asia/Ho_Chi_Minh")

def now_vn():
    return datetime.now(vn_tz)

class BlockedUserLog(db.Model):
    __tablename__ = 'blocked_user_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    block_time = db.Column(db.DateTime, default=now_vn)  # ✅ Lưu theo giờ VN
    time_slot = db.Column(db.String, nullable=False)

