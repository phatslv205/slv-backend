from extensions import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    txn_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.String(20), nullable=False)
    package = db.Column(db.String(50), nullable=False)
    method = db.Column(db.String(50), nullable=False)
    referral_code = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
