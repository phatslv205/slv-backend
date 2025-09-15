from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(async_mode="threading")
login_manager = LoginManager()

def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "login"  

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)
