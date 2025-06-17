from datetime import datetime
from models.user import User
from extensions import db



def is_vip(username):
    if username == "admin":
        return True

    user = User.query.filter_by(email=username).first()
    if not user or not user.vip_until:
        return False

    try:
        return user.vip_until >= datetime.now().date()
    except:
        return False
