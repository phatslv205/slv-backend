from flask import Flask
from flask_migrate import Migrate
from alembic import command
from alembic.config import Config
import os

# 🔧 Khởi tạo Flask app (nếu dùng factory thì sửa lại)
from extensions import db
from models import *  # đảm bảo tất cả models được import
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:slv2025@localhost:5432/slv_users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Load config Alembic
alembic_cfg = Config("migrations/alembic.ini")  # Đường dẫn đến alembic.ini

# 📦 Tạo file migration như `flask db migrate -m "init"`
with app.app_context():
    message = "manual init"
    command.revision(config=alembic_cfg, message=message, autogenerate=True)
    print("✅ File migration đã tạo thành công trong versions/")
