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
@jwt_required()
def get_post(post_id):
    #获取用户名
    user_id = int(get_jwt_identity())
    
    #获取post id
    post = Post.query.get_or_404(post_id)
    
    #如果post的作者名与用户名不匹配，返回错误
    if post.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

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
    data = request.get_json()
    title = data.get("title")
    body = data.get("body")
    user_id = get_jwt_identity()

    new_post = Post(title=title, body=body, author_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"msg": "Post created", "id": new_post.id}), 201

#更新post
@blog_bp.route("/<int:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)

    if post.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    post.title = data.get("title", post.title)
    post.body = data.get("body", post.body)
    db.session.commit()

    return jsonify({"msg": "Post updated"}), 200

#删除post
@blog_bp.route("/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)

    if post.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"msg": "Post deleted"}), 200
