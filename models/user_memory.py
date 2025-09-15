from datetime import datetime
from extensions import db
from datetime import datetime
import pytz

VIETNAM_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

class UserMemoryItem(db.Model):
    __tablename__ = 'user_memory_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    encrypted_password = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.now(VIETNAM_TZ), onupdate=datetime.now(VIETNAM_TZ))

