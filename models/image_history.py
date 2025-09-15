from datetime import datetime
from extensions import db

class ImageHistory(db.Model):
    __tablename__ = 'image_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    source = db.Column(db.String, default="manual")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    message_index = db.Column(db.Integer)

    def __repr__(self):
        return f"<ImageHistory {self.prompt[:30]}...>"
