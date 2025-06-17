import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:slv2025@localhost/slv_users'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'slv-secret-key'  # hoặc dùng os.environ
 