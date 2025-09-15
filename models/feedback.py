from extensions import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"))
    session_id = db.Column(db.String(36))
    stars = db.Column(db.Integer)  # từ 1–5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_personality = db.Column(db.String(100))
    package_type = db.Column(db.String(50))  # gói GPT/Lite nếu muốn lưu

    def __repr__(self):
        return f"<Feedback {self.stars}⭐ - {self.user_id}>"
