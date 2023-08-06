# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import re
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, jsonify
from flask_login import login_required, current_user

from blog.extensions import db, minio
from blog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from blog.models import Post, Category, Comment, Link
from blog.utils import redirect_back, allowed_file
from sqlalchemy import and_

admin_bp = Blueprint('admin', __name__)


def get_img_name(body):
    images = [i[:-1].split('/')[-1]
              for i in re.findall('!\\[[^\\]]*\\]\\([^\\)]+\\)', body)]
    if len(images) > 0:
        return ', '.join(images)
    else:
        return None


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.body.data
        current_user.img_name = get_img_name(form.body.data)
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.about'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.body.data = current_user.about
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        img_name = get_img_name(body)
        post = Post(title=title, body=body,
                    category=category, img_name=img_name)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        post.img_name = get_img_name(post.body)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    img_name = post.img_name
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    if img_name != None:
        img_list = img_name.split(', ')
        for img in img_list:
            minio.remove_object(current_app.config['MINIO_BUCKET'], img)
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
    # 'all', 'unreviewed', 'admin'
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_MANAGE_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(
        Comment.timestamp.asc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/check', methods=['POST'])
@login_required
def check_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/<int:total>/post/check', methods=['POST'])
@login_required
def check_post_comment(comment_id, total):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    page = (total-1)//current_app.config['BLOG_COMMENT_PER_PAGE'] + 1
    if not total:
        page = 1
    return redirect('/post/%s?page=%s#comment-%s'%(comment.post.id, page, comment_id))


@admin_bp.route('/comment/<int:comment_id>/details')
@login_required
def details_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    position = Comment.query.filter(and_(Comment.post_id == comment.post.id, Comment.id <= comment_id)).count()
    page = (position-1)//current_app.config['BLOG_COMMENT_PER_PAGE'] + 1
    return redirect('/post/%s?page=%s#comment-%s'%(comment.post.id, page, comment_id))
    


@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/<int:total>/post/delete', methods=['POST'])
@login_required
def delete_post_comment(comment_id, total):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    last_comment = Comment.query.filter(and_(Comment.post_id == post_id, Comment.id < comment.id)).order_by(Comment.id.desc()).first()
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    if total-1==0:
        return redirect_back()
    if not last_comment:
        return redirect('/post/%s#comments'%post_id)
    position = Comment.query.filter(and_(Comment.post_id == post_id, Comment.id <= last_comment.id)).count() # 上一条记录为第几条记录
    page = (position-1)//current_app.config['BLOG_COMMENT_PER_PAGE'] + 1
    return redirect('/post/%s?page=%s#comment-%s'%(post_id, page, last_comment.id))

@admin_bp.route('/category/manage')
@login_required
def manage_category():
    return render_template('admin/manage_category.html')


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('blog.index'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))

    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/link/manage')
@login_required
def manage_link():
    return render_template('admin/manage_link.html')


@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        is_navigator = form.url.is_navigator
        link = Link(name=name, url=url, is_navigator=is_navigator)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'success')
        return redirect(url_for('.manage_link'))
    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    form = LinkForm()
    link = Link.query.get_or_404(link_id)
    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        link.is_navigator = form.is_navigator.data
        db.session.commit()
        flash('Link updated.', 'success')
        return redirect(url_for('.manage_link'))
    form.name.data = link.name
    form.url.data = link.url
    form.is_navigator.data = link.is_navigator
    return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted.', 'success')
    return redirect(url_for('.manage_link'))


@admin_bp.route('/upload', methods=['POST'])
def upload_image():
    f = request.files.get('file')
    if not allowed_file(f.filename):
        return jsonify({
            'success': False,
            'error': 'This image type is not allowed.'
        })
    now = datetime.now()  # 获得当前时间
    timestr = now.strftime("%Y_%m_%d_%H_%M_%S")
    f.filename = timestr+'.'+f.filename.split('.')[-1]

    minio.put_object(
        current_app.config['MINIO_BUCKET'], f.filename, f, -1, part_size=5*1024*1024)
    url = current_app.config['MINIO_PROTOCOL']+'://'+current_app.config['MINIO_HOST'] + ':' +  current_app.config['MINIO_PORT'] + \
        '/'+current_app.config['MINIO_BUCKET']+'/'+f.filename

    return jsonify({
        'success': True,
        'url': url
    })
