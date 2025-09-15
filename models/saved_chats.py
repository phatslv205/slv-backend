# models/saved_chat.py
from datetime import datetime
from extensions import db

class SavedChat(db.Model):
    __tablename__ = "saved_chats"

    id = db.Column(db.String, primary_key=True)  # UUID
    user_id = db.Column(db.String, nullable=False)
    session_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, default="Đoạn chat đã lưu")
    messages = db.Column(db.JSON, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
