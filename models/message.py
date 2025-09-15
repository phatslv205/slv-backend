from extensions import db
from datetime import datetime
import uuid
from datetime import datetime, timedelta

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_key = db.Column(db.String(255), nullable=False)  
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    image_urls = db.Column(db.JSON) 
    voice_url = db.Column(db.String(255))
    video_url = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=7))
    receiver = db.Column(db.String(50), nullable=False)
    read = db.Column(db.Boolean, default=False)
    reply_to = db.Column(db.JSON, nullable=True)
    deleted_for = db.Column(db.JSON, default=list)
    unsent = db.Column(db.Boolean, default=False)

