# models/friend.py
from extensions import db

class Friend(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    friend_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)

    # Không cho trùng (user_id, friend_id)
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='_user_friend_uc'),)
