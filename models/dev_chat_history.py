from datetime import datetime
from extensions import db
class DevChatHistory(db.Model):
    __tablename__ = 'dev_chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'), nullable=False)
    session_id = db.Column(db.String, nullable=False)  # UUID của session hoặc đoạn chat dev
    history = db.Column(db.JSON, nullable=False)       # Lưu dạng [{role:..., content:...}]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DevChatHistory user_id={self.user_id} session_id={self.session_id}>"
