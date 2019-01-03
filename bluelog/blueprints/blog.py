from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user
from bluelog.models import Post, Category, Comment, Admin
from bluelog.forms import AdminCommentForm, CommentForm
from bluelog.extensions import db

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/', defaults={'page': 1})
@blog_bp.route('/page/<int:page>')
def index(page):
    page = page
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(
        Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    admin = Admin.query.first()
    return render_template('blog/index.html', admin=admin, posts=posts, pagination=pagination)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>', defaults={'page': 1})
@blog_bp.route('/category/<int:category_id>/page/<int:page>')
def show_category(category_id, page):
    category = Category.query.get(category_id)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(
        Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', defaults={'page': 1}, methods=['GET', 'POST'])
@blog_bp.route('/post/<int:post_id>/page/<int:page>', methods=['GET', 'POST'])
def show_post(post_id, page):
    post = Post.query.get_or_404(post_id)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(
        Comment.timestamp.asc()).paginate(page, per_page=per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_username
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed
        )

        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            
        db.session.add(comment)
        db.session.commit()
        
        if current_user.is_authenticated:
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed', 'info')
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, comments=comments, form=form)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')
