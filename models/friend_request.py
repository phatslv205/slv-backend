from extensions import db
from datetime import datetime

class FriendRequest(db.Model):
    __tablename__ = "friend_requests"
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    to_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)


    created_at = db.Column(db.DateTime, default=datetime.utcnow)
