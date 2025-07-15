class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"  # 使用 SQLite 测试
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super-secret"  # ⚠️ 建议后期通过环境变量设置

    JWT_IDENTITY_CLAIM = "sub"