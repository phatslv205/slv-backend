from extensions import db
from datetime import datetime

class Inbox(db.Model):
    __tablename__ = "inbox"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.user_id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(20))  # ví dụ: 'admin_reply', 'announcement'
