from app import app
from extensions import db
from models.user import User

with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"🧑 {u.username} - VIP: {u.vip_gpt}")
