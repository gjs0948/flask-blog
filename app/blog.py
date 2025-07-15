from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity

blog_bp = Blueprint("blog", __name__)

@blog_bp.route("/", methods=["GET"])
@jwt_required()
def list_posts():
    user_id = get_jwt_identity()
    posts = Post.query.filter_by(author_id=user_id).all()
    return jsonify([{"id": p.id, "title": p.title, "body": p.body} for p in posts]), 200


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
