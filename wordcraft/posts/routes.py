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
        # Update the title and content
        post.title = form.title.data
        post.content = form.content.data
        
        # Update the image if a new one is provided
        if form.image.data:
            picture_file = save_picture(form.image.data)
            post.image_file = picture_file
        
        # Commit the changes to the database
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    
    elif request.method == 'GET':
        # Pre-fill the form with the current post data
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

