from models.user import User
from extensions import db
from sqlalchemy import text
from run import app  # Giả sử app nằm trong run.py

with app.app_context():
    # Lấy danh sách cột trong model
    model_columns = set(c.name for c in User.__table__.columns)

    # Lấy danh sách cột thực tế từ PostgreSQL
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        actual_columns = set(row[0] for row in result)

    # So sánh
    missing_columns = model_columns - actual_columns

    print("🔥 Các cột thiếu trong bảng `users`:")
    for col in missing_columns:
        print(f"- {col}")
