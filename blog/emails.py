# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread
from flask import url_for, current_app
from flask_mail import Message
from blog.extensions import mail
from markdown2 import markdown
from datetime import datetime
import time


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def body_to_html(text):
    return markdown(text, extras=[
        'fenced-code-blocks', 'highlightjs-lang', 'tables'])


def get_time(timestamp):
    now_stamp = time.time()
    local_time = datetime.fromtimestamp(now_stamp)
    utc_time = datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    timestamp += offset
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def send_new_comment_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post.id,
                       _external=True) + '#comment-%s'%comment.id
    body = body_to_html(comment.body)
    send_mail(subject='[New comment] %s' % comment.post.title, to=current_app.config['BLOG_EMAIL'],
              html='''
                    <p>
                        %s<small style="color: #868e96">&lt;%s&gt;&nbsp;%s</small>
                    </p>
                        %s
                    <hr/>
                    <p>
                        click the link below to check:
                    </p>
                    <p><a href="%s">%s</a></p>
                    <p><small style="color: #868e96">Do not reply this email.</small></p>
                ''' % (comment.author, comment.email, get_time(comment.timestamp), body, post_url, post_url))


def send_new_reply_email(comment, reply):
    post_url = url_for('blog.show_post', post_id=comment.post_id,
                       _external=True) + '#comment-%s'%reply.id
    reply_body = body_to_html(reply.body)
    comment_body = body_to_html(comment.body)
    send_mail(subject='[New reply] %s' % comment.post.title, to=comment.email,
              html='''
                    <p>
                        %s<small style="color: #868e96">&lt;%s&gt;&nbsp;%s</small>
                    </p>
                    %s
                    <div style="color: #868e96; font-style: italic; margin-top: 14px; margin-left: 40px;">
                        <p>
                            replied comment:
                        <p>
                        <p>
                            %s<small style="color: #868e96">&lt;%s&gt;&nbsp;%s</small>
                        </p>
                        %s
                    </div>
                    <hr />
                    <p>
                        click the link below to check:
                    </p>
                    <p><a href="%s">%s</a></p>
                    <p><small style="color: #868e96">Do not reply this email.</small></p>
                   ''' % (reply.author, reply.email, get_time(reply.timestamp), reply_body, comment.author, comment.email, get_time(comment.timestamp), comment_body, post_url, post_url))
