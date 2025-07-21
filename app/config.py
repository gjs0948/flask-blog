import os
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"  # 使用 SQLite 测试
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-for-dev")  # 默认值仅用于开发

    JWT_IDENTITY_CLAIM = "sub"