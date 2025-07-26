from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Comment
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone

comment_bp = Blueprint("comment",__name__)

#获取某个post下所有comment
@comment_bp.route("/",methods=["GET"])
def list_comments():
    #获取postid
    post_id = request.args.get("post_id",type=int)
    
    #如果没有postid，返回400
    if not post_id:
        return {"message": "post_id is required."}, 400
    
    #返回所有comment
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.create_at.desc()).all()
    return jsonify([
        {
            "id": c.id,
            "content": c.content,
            "user_id": c.user_id,
            "post_id": c.post_id,
            "username":c.author.username,
            "create_at": c.create_at.isoformat() if c.create_at else None,
            "update_at":  c.update_at.isoformat() if c.update_at else None
        } for c in comments
    ])

# 创建comment
@comment_bp.route("/", methods=["POST"])
@jwt_required()
def create_comment():
    #获取数据
    data = request.get_json()
    
    #获取内容，postid，userid
    content = data.get("content")
    post_id = data.get("post_id")
    user_id = get_jwt_identity()
    
    #没有内容或者postid，返回400
    if not content or not post_id:
        return {"message": "Content and post_id are required."}, 400
    
    #创建comment条目
    comment = Comment(content=content, user_id=user_id, post_id=post_id)
    
    #添加新comment到数据库
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "create_at": comment.create_at
    }), 201

# 更新comment
@comment_bp.route("/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    #获取数据
    data = request.get_json()

    #获取修改内容
    content = data.get("content")
    
    #获取用户id，由于get_jwt_identity返回的是字符串，而post表中的author_id是int型，所以需要将字符串转化为整型数字
    user_id = int(get_jwt_identity())

    #获取数据库中的comment
    comment = Comment.query.get_or_404(comment_id)

    #如果comment的作者与userid不匹配，返回403
    if comment.user_id != user_id:
        return {"message": "Permission denied."}, 403
    if not content:
        return {"message": "Content is required."}, 400
    
    #更新comment内容
    comment.content = content
    comment.update_at = datetime.now(timezone.utc)

    #提交数据库
    db.session.commit()
    
    #返回json格式数据
    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "update_at": comment.update_at
    }), 200

# 删除comment
@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    #获取用户id，由于get_jwt_identity返回的是字符串，而post表中的author_id是int型，所以需要将字符串转化为整型数字
    user_id = int(get_jwt_identity())

    #获取数据库中的comment
    comment = Comment.query.get_or_404(comment_id)

    #如果comment的作者与userid不匹配，返回403
    if comment.user_id != user_id:
        return {"message": "Permission denied."}, 403
    
    #在数据库中删除comment
    db.session.delete(comment)

    #提交
    db.session.commit()
    return {"message": "Comment deleted."}, 200