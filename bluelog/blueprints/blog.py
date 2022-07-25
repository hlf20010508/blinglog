# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user
from bluelog.emails import send_new_comment_email, send_new_reply_email
from bluelog.extensions import db
from bluelog.forms import CommentForm, AdminCommentForm
from bluelog.models import Post, Category, Comment, Admin
from bluelog.utils import redirect_back
import bluelog.OSS_minio as oss
from markdown2 import markdown
from sqlalchemy import or_

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(
        Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    for i in range(len(posts)):
        posts[i].body = markdown(posts[i].body)

    post_with_img = Post.query.filter(Post.img_name).all()
    admin_with_img = Admin.query.filter(Admin.img_name).all()
    img_list = [p.img_name for p in post_with_img] + \
        [a.img_name for a in admin_with_img]
    img_name = ', '.join(img_list)  # 连接每条记录的所有图片名字符串
    img_list = img_name.split(', ')  # 拆分得到所有图片名单独的字符串

    client = oss.Client()
    img_all = client.list()

    for i in img_all:
        if i not in img_list:
            client.remove(i)

    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    about = markdown(current_user.about, extras=[
        'fenced-code-blocks', 'highlightjs-lang', 'tables'])
    return render_template('blog/about.html', about=about)


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(
        Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
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
            from_admin=from_admin, post=post, reviewed=reviewed)
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment, comment)
        db.session.add(comment)
        db.session.commit()
        if not current_user.is_authenticated:  # send message based on authentication status
            # send notification email to admin
            send_new_comment_email(comment)
        flash('Comment published.', 'success')
        return redirect(url_for('.show_post', post_id=post_id))

    post.body = markdown(
        post.body, extras=['fenced-code-blocks', 'highlightjs-lang', 'tables'])
    for comment in comments:
        comment.body = markdown(
            comment.body, extras=['fenced-code-blocks', 'highlightjs-lang', 'tables'])
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response


@blog_bp.route('/search')
def search():
    content = request.args.get('content').strip()
    # if content == '':
    #     flash('Enter something you want to search.', 'warning')
    #     return redirect_back()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    post_query=Post.query.filter(or_(Post.body.like('%'+content+'%'), Post.title.like('%'+content+'%')))
    comment_query=Post.query.join(Comment).filter(Comment.body.like('%'+content+'%'))
    query=post_query.union(comment_query)
    pagination = query.paginate(page, per_page)
    results = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=results)