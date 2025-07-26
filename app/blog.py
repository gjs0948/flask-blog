from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity

blog_bp = Blueprint("blog", __name__)

#返回所有文章
@blog_bp.route("/", methods=["GET"])
def list_posts():
    posts = Post.query.order_by(Post.id.desc()).all()  # 默认返回所有文章

    return jsonify([{"id": p.id, 
                     "title": p.title, 
                     "body": p.body,
                     "author_id":p.author_id,
                     "author_name":p.author.username
                     } for p in posts]), 200

#返回指定文章标题与内容
@blog_bp.route("/<int:post_id>",methods=["GET"])
def get_post(post_id):
    #获取post id
    post = Post.query.get_or_404(post_id)

    #返回json格式数据
    return jsonify({
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "author_id": post.author_id
    }), 200

#创建post
@blog_bp.route("/", methods=["POST"])
@jwt_required()
def create_post():
    #获取data
    data = request.get_json()
    
    #获取标题与内容
    title = data.get("title")
    body = data.get("body")

    #获取创建post的用户
    user_id = get_jwt_identity()

    #创建新的post条目
    new_post = Post(title=title, body=body, author_id=user_id)
    
    #添加新post到数据库
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"msg": "Post created", "id": new_post.id}), 201

#更新post
@blog_bp.route("/<int:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    #获取用户id，由于get_jwt_identity返回的是字符串，而post表中的author_id是int型，所以需要将字符串转化为整型数字
    user_id = int(get_jwt_identity())

    #获取数据库中的post
    post = Post.query.get_or_404(post_id)

    #识别是否为post作者
    if post.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    #获取数据
    data = request.get_json()
    
    #修改post标题与内容
    post.title = data.get("title", post.title)
    post.body = data.get("body", post.body)
    db.session.commit()

    return jsonify({"msg": "Post updated"}), 200

#删除post
@blog_bp.route("/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    #获取用户id，由于get_jwt_identity返回的是字符串，而post表中的author_id是int型，所以需要将字符串转化为整型数字
    user_id = int(get_jwt_identity())

    #获取数据库中的post
    post = Post.query.get_or_404(post_id)
    
    #识别是否为post作者
    if post.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    #从数据库中删除post
    db.session.delete(post)
    db.session.commit()

    return jsonify({"msg": "Post deleted"}), 200
