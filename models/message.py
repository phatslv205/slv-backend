from extensions import db
from datetime import datetime
import uuid

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_key = db.Column(db.String(255), nullable=False)  # ví dụ: user1__user2
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    image_urls = db.Column(db.JSON)  # lưu danh sách ảnh
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)