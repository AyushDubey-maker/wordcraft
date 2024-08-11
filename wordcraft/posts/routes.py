# from flask import (render_template, url_for, flash,
#                    redirect, request, abort, Blueprint)
# from flask_login import current_user, login_required
# from wordcraft import db
# from wordcraft.models import Post
# from wordcraft.posts.forms import PostForm

# posts = Blueprint('posts', __name__)


# @posts.route("/post/new", methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         post = Post(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('main.home'))
#     return render_template('create_post.html', title='New Post',
#                            form=form, legend='New Post')
import os
import secrets
from flask import (render_template, url_for, flash, 
                   redirect, request, abort, Blueprint, current_app, jsonify)
from flask_login import current_user, login_required
from wordcraft import db
from wordcraft.models import Post,Likes
from wordcraft.posts.forms import PostForm
from PIL import Image

posts = Blueprint('posts', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/post_images', picture_fn)

    # Resize the image before saving
    output_size = (1080, 1080) 
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data)
            post = Post(title=form.title.data, content=form.content.data, image_file=picture_file, author=current_user)
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
     # Fetch the trending post (most liked/disliked)
    trending_post = Post.query.order_by(Post.likes_count.desc()).first()

    # Fetch the latest two posts in descending order
    latest_posts = Post.query.order_by(Post.date_posted.desc(), Post.id.desc()).limit(2).all()
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post', trending_post=trending_post, latest_posts=latest_posts)



@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
     # Fetch the trending post (most liked/disliked)
    trending_post = Post.query.order_by(Post.likes_count.desc()).first()

    # Fetch the latest two posts in descending order
    latest_posts = Post.query.order_by(Post.date_posted.desc(), Post.id.desc()).limit(2).all()
    return render_template('post.html', title=post.title, post=post, trending_post=trending_post, latest_posts=latest_posts)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

# # Like Dislike Functionality

# @posts.route("/post/like/<int:post_id>/<action>", methods=['POST'])
# @login_required
# def like_post(post_id, action):
#     post = Post.query.get_or_404(post_id)
    
#     if action == 'like':
#         existing_like = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=True).first()
#         if existing_like:
#             db.session.delete(existing_like)
#             post.likes_count -= 1
#         else:
#             existing_dislike = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=False).first()
#             if existing_dislike:
#                 db.session.delete(existing_dislike)
#                 post.dislikes_count -= 1
#             new_like = Likes(user_id=current_user.id, post_id=post_id, is_like=True)
#             db.session.add(new_like)
#             post.likes_count += 1
            
#     elif action == 'dislike':
#         existing_dislike = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=False).first()
#         if existing_dislike:
#             db.session.delete(existing_dislike)
#             post.dislikes_count -= 1
#         else:
#             existing_like = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=True).first()
#             if existing_like:
#                 db.session.delete(existing_like)
#                 post.likes_count -= 1
#             new_dislike = Likes(user_id=current_user.id, post_id=post_id, is_like=False)
#             db.session.add(new_dislike)
#             post.dislikes_count += 1
    
#     db.session.commit()
    
#     return jsonify({
#         'like_count': post.likes_count,
#         'dislike_count': post.dislikes_count
#     })

# @posts.route("/user_liked/<int:post_id>")
# @login_required
# def user_liked(post_id):
#     liked = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=True).first() is not None
#     return jsonify({'liked': liked})

# @posts.route("/user_disliked/<int:post_id>")
# @login_required
# def user_disliked(post_id):
#     disliked = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, is_like=False).first() is not None
#     return jsonify({'disliked': disliked})