# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import sys
import config as myconfig

config = myconfig.load()

minio_protocol = 'https' if config['secure_minio'] else 'http'
minio_port = config['host_minio'].split(':')[1]
minio_host = '%s://127.0.0.1:%s/%s' % (minio_protocol, minio_port, config['bucket']
                                       ) if config['local_minio'] else minio_protocol+'://'+config['host_minio']+'/'+config['bucket']

port = config['host_mysql'].split(':')[1]
mysql_host = config['username_mysql']+':'+config['password_mysql']+'@'+'127.0.0.1:'+port+'/' + \
    config['database'] if config['local_mysql'] else config['username_mysql'] + \
    ':'+config['password_mysql']+'@' + \
    config['host_mysql']+'/'+config['database']

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://"+mysql_host

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
    BLUELOG_POST_PER_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    BLUELOG_THEMES = {'perfect_blue': 'Perfect Blue',
                      'black_swan': 'Black Swan'}
    BLUELOG_SLOW_QUERY_THRESHOLD = 1

    # BLUELOG_UPLOAD_PATH = os.path.join(basedir, 'uploads')

    BLUELOG_MINIO_PATH = minio_host
    BLUELOG_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
