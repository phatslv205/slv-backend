from datetime import datetime, timedelta
from models import ChatHistory
from extensions import db

def delete_old_chat_history():
    threshold = datetime.utcnow() - timedelta(days=30)
    deleted = ChatHistory.query.filter(ChatHistory.timestamp < threshold).delete()
    db.session.commit()
    print(f"✅ Đã xoá {deleted} tin nhắn cũ trước ngày {threshold.date()}.")

def run_delete_old_chat_history(app):
    with app.app_context():
        delete_old_chat_history()
