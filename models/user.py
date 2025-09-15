from extensions import db
from datetime import datetime
import uuid
from models.friend import Friend
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
from datetime import date
import random
import string
def generate_referral_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
blocked_users = db.Table(
    "blocked_users",
    db.Column("user_id", db.String(36), db.ForeignKey("users.user_id")),
    db.Column("blocked_id", db.String(36), db.ForeignKey("users.user_id"))
)
class User(db.Model, UserMixin):
    __tablename__ = "users"
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    is_blocked = db.Column(db.Boolean, default=False)
    fullname = db.Column(db.String(255))
    bio = db.Column(db.String(500))
    bio_updated_at = db.Column(db.DateTime, default=None)
    vip_gpt = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    privacy = db.Column(JSON, default={})
    otp_code = db.Column(db.String(10))
    online = db.Column(db.Boolean, default=False)
    wants_verification = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(255), default="")
    free_gpt_uses = db.Column(db.Integer, default=0)
    gpt_usage_today = db.Column(db.Integer, default=0)
    gpt_usage_date = db.Column(db.String(10))  # Format YYYY-MM-DD
    over_quota_block = db.Column(db.Boolean, default=False)
    over_quota_block_at = db.Column(db.DateTime, nullable=True)
    gpt_unlimited = db.Column(db.Boolean, default=False)
    email_temp = db.Column(db.String, nullable=True)
    ai_personality = db.Column(db.String(100))  # VD: "Drama Queen"
    ai_system_prompt = db.Column(db.Text)       # prompt tương ứng
    ai_personality_rolls_left = db.Column(db.Integer, default=5)  # số lượt random còn lại
    ai_personality_rolls_reset_at = db.Column(db.DateTime, default=datetime.utcnow)
    daily_fallback_uses = db.Column(db.Integer, default=0)
    daily_fallback_date = db.Column(db.String)
    image_quota_today = db.Column(db.Integer, default=10)
    image_quota_reset_at = db.Column(db.DateTime)
    vip_until_gpt = db.Column(db.DateTime, nullable=True)
    vip_until_lite = db.Column(db.DateTime, nullable=True)
    vip_gpt_ai = db.Column(db.Boolean, default=False)
    vip_ai_lite = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    lite_usage = db.Column(db.Integer, default=0)
    lite_date = db.Column(db.String(20))
    last_lite_free_date = db.Column(db.String(20))
    pending_messages = db.Column(db.Integer, default=0)
    last_sent_at = db.Column(db.DateTime, default=None)
    vip_until_gpt = db.Column(db.DateTime)
    smartdoc_usage_today = db.Column(db.Integer, default=0)
    smartdoc_last_used_date = db.Column(db.Date, default=date.today)
    cs_flatline_count = db.Column(db.Integer, default=0)
    cs_mindtwist_count = db.Column(db.Integer, default=0)
    cs_hexlock_count = db.Column(db.Integer, default=0)
    cs_lineslicer_count = db.Column(db.Integer, default=0)
    cs_usage_reset_at = db.Column(db.Date, default=date.today)
    referral_code = db.Column(db.String(10), unique=True, nullable=True, default=generate_referral_code)
    referral_code_used = db.Column(db.String(20), nullable=True)
    reward_fullname = db.Column(db.String(100))
    reward_bank = db.Column(db.String(100))
    reward_stk = db.Column(db.String(30))
    has_seen_intro = db.Column(db.Boolean, default=False, nullable=False)
    image_generation_used = db.Column(db.Integer, default=0)  
    image_generation_blocked = db.Column(db.Boolean, default=False)
    normalized_email = db.Column(db.String(120), unique=True, nullable=False)
    last_pending_reset = db.Column(db.DateTime, nullable=True)

    friends = db.relationship(
    'Friend',
        foreign_keys='Friend.user_id',
        backref='owner',
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
    # 👇 THÊM vào trong class User:
    blocked_users = db.relationship(
        'User',
        secondary=blocked_users,
        primaryjoin=(user_id == blocked_users.c.user_id),
        secondaryjoin=(user_id == blocked_users.c.blocked_id),
        backref='blocked_by'
    )
    
    def is_active(self):
            return not self.is_blocked 
    def get_id(self):
            return str(self.user_id)