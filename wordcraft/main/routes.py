# from flask import render_template, request, Blueprint, jsonify
# from flask_login import current_user, login_required
# from flaskblog import db
# from flaskblog.models import Post, Likes




# main = Blueprint('main', __name__)
# posts = Blueprint('posts', __name__)

# @main.route("/")
# @main.route("/home")
# def home():
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
#     return render_template('home.html', posts=posts, user_liked=user_liked, user_disliked=user_disliked)


# def user_liked(post_id):
#     if current_user.is_authenticated:
#         return Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=True).first() is not None
#     return False

# def user_disliked(post_id):
#     if current_user.is_authenticated:
#         return Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=False).first() is not None
#     return False


# @main.route("/about")
# def about():
#     return render_template('about.html', title='About')

from flask import render_template, request, Blueprint, jsonify, redirect, url_for
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Likes

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    # Fetch the trending post (most liked/disliked)
    trending_post = Post.query.order_by(Post.likes_count.desc()).first()

    # Fetch the latest two posts in descending order
    latest_posts = Post.query.order_by(Post.date_posted.desc(), Post.id.desc()).limit(2).all()

    return render_template('home.html', posts=posts, user_liked=user_liked, user_disliked=user_disliked, trending_post=trending_post, latest_posts=latest_posts)

def user_liked(post_id):
    if current_user.is_authenticated:
        return Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=True).first() is not None
    return False

def user_disliked(post_id):
    if current_user.is_authenticated:
        return Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=False).first() is not None
    return False

@main.route("/home/like/<int:post_id>", methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Likes.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_like:
        if existing_like.is_like:
            # User is trying to like an already liked post, so we remove the like
            db.session.delete(existing_like)
            post.likes_count -= 1
        else:
            # User is switching from dislike to like
            existing_like.is_like = True
            post.likes_count += 1
            post.dislikes_count -= 1
    else:
        # User is liking the post for the first time
        new_like = Likes(user_id=current_user.id, post_id=post_id, is_like=True)
        db.session.add(new_like)
        post.likes_count += 1
    
    db.session.commit()
    return jsonify({'success': True})

@main.route("/home/dislike/<int:post_id>", methods=['POST'])
@login_required
def dislike_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Likes.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_like:
        if not existing_like.is_like:
            # User is trying to dislike an already disliked post, so we remove the dislike
            db.session.delete(existing_like)
            post.dislikes_count -= 1
        else:
            # User is switching from like to dislike
            existing_like.is_like = False
            post.likes_count -= 1
            post.dislikes_count += 1
    else:
        # User is disliking the post for the first time
        new_dislike = Likes(user_id=current_user.id, post_id=post_id, is_like=False)
        db.session.add(new_dislike)
        post.dislikes_count += 1
    
    db.session.commit()
    return jsonify({'success': True})

@main.route("/home/post/<int:post_id>/counts")
def get_post_counts(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({'like_count': post.likes_count, 'dislike_count': post.dislikes_count})

@main.route("/about")
def about():
     # Fetch the trending post (most liked/disliked)
    trending_post = Post.query.order_by(Post.likes_count.desc()).first()

    # Fetch the latest two posts in descending order
    latest_posts = Post.query.order_by(Post.date_posted.desc(), Post.id.desc()).limit(2).all()
    return render_template('about.html', title='About', trending_post=trending_post, latest_posts=latest_posts)



