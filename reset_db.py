from run import app
from extensions import db
from models.user import User

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Đã xóa và tạo lại bảng thành công.")
