from extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import JSON
blocked_users = db.Table(
    "blocked_users",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("blocked_id", db.Integer, db.ForeignKey("users.id"))
)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    is_blocked = db.Column(db.Boolean, default=False)
    fullname = db.Column(db.String(255))
    bio = db.Column(db.String(500))
    bio_updated_at = db.Column(db.DateTime, default=None)
    birthday = db.Column(db.String(20))
    vip_gpt = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    privacy = db.Column(JSON, default={})
    user_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    otp_code = db.Column(db.String(10))
    online = db.Column(db.Boolean, default=False)
    wants_verification = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(255), default="")
    free_gpt_uses = db.Column(db.Integer, default=0)
    gpt_usage_today = db.Column(db.Integer, default=0)
    gpt_usage_date = db.Column(db.String(10))  # Format YYYY-MM-DD
    gpt_unlimited = db.Column(db.Boolean, default=False)
    email_temp = db.Column(db.String, nullable=True)
    phone = db.Column(db.String(20), nullable=True)

     

    # Các cột VIP
    vip_until_gpt = db.Column(db.DateTime, nullable=True)
    vip_until_lite = db.Column(db.DateTime, nullable=True)
    
    vip_gpt_ai = db.Column(db.Boolean, default=False)
   
    vip_ai_lite = db.Column(db.Boolean, default=False)
    
    is_verified = db.Column(db.Boolean, default=False, nullable=False)


    lite_usage = db.Column(db.Integer, default=0)
    lite_date = db.Column(db.String(20))
    last_lite_free_date = db.Column(db.String(20))
    friends = db.relationship(
        'Friend',
        primaryjoin="User.user_id == Friend.user_id",
        backref="user",
        lazy='dynamic'
    )
