from run import app
from extensions import db
from flask_migrate import upgrade

with app.app_context():
    upgrade()
