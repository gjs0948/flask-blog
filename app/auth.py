from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    #获取注册数据
    data = request.get_json()
    
    #获取注册用户名
    username = data.get("username")
    
    #获取注册密码
    password = data.get("password")

    #如果数据库中已有同名用户，返回错误
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    #使用bcrypt生成加密的密码
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    
    #使用加密密码与用户名创建新的用户实例
    new_user = User(username=username, password=hashed_pw)
    
    #提交用户实例到数据库
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    #获取登录数据
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    #在数据库中查找用户
    user = User.query.filter_by(username=username).first()
    
    #如果用户存在并且提供的密码正确，返回JWT
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
