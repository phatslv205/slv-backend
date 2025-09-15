from extensions import db
from datetime import datetime
from datetime import datetime, timezone
class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    session_id = db.Column(db.String, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    reply_to = db.Column(db.Text)
    reply_to_content = db.Column(db.Text)
    is_saved = db.Column(db.Boolean, default=False)
    role = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
   

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    title = db.Column(db.String, default="Đoạn chat mới")
   