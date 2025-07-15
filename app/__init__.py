from flask import Flask
from .extensions import db, migrate, bcrypt, jwt, cors
from .auth import auth_bp
from .blog import blog_bp
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化 Flask 扩展
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(blog_bp, url_prefix="/api/posts")

    return app
