# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import json


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')  # 自定义csrf secret key

    DEBUG_TB_INTERCEPT_REDIRECTS = False  # 禁止flask debug toolbar拦截redirect

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_SLOW_QUERY_THRESHOLD = 1  # sql 慢查询阀值
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 5,
        'pool_timeout': 10,
        'pool_recycle': 3600,
    }
    
    BLOG_POST_PER_PAGE = 10
    BLOG_MANAGE_POST_PER_PAGE = 15
    BLOG_COMMENT_PER_PAGE = 15
    BLOG_MANAGE_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    BLOG_THEMES = {'perfect_blue': 'Perfect Blue',
                      'black_swan': 'Black Swan'}
    BLOG_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    except:
        try:
            config = {
                'host_mysql': os.environ['host_mysql'],
                'port_mysql': os.environ['port_mysql'],
                'username_mysql': os.environ['username_mysql'],
                'password_mysql': os.environ['password_mysql'],
                'database_mysql': os.environ['database_mysql'],
                'host_minio': os.environ['host_minio'],
                'port_minio': os.environ['port_minio'],
                'protocol_minio': os.environ['protocol_minio'],
                'local_minio': True if os.environ['local_minio']=='true' else False,
                'username_minio': os.environ['username_minio'],
                'password_minio': os.environ['password_minio'],
                'bucket_minio': os.environ['bucket_minio'],
                'host_email': os.environ.get('host_email', None),
                'port_email': os.environ.get('port_email', None),
                'ssl_email': True if os.environ.get('ssl_email', False)=='true' else False,
                'tls_email': True if os.environ.get('tls_email', False)=='true' else False,
                'address_email': os.environ.get('address_email', None),
                'password_email': os.environ.get('password_email', None),
                'receive_email': os.environ.get('receive_email', None),
            }
        except:
            pass

    try:
        host_mysql = config['host_mysql']
        port_mysql = config['port_mysql']
        username_mysql = config['username_mysql']
        password_mysql = config['password_mysql']
        database_mysql = config['database_mysql']
        endpoint_mysql = username_mysql + ':' + password_mysql + \
            '@' + host_mysql + ':' + port_mysql + '/' + database_mysql

        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://"+endpoint_mysql
    except:
        SQLALCHEMY_DATABASE_URI = None
        print('\nconfiguration of mysql not found.')
        print('Run command: flask setdb\n')

    try:
        host_minio = config['host_minio']
        port_minio = config['port_minio']
        minio_protocol = config['protocol_minio']
        local_minio = config['local_minio']
        username_minio = config['username_minio']
        password_minio = config['password_minio']
        bucket_minio = config['bucket_minio']
        endpoint_minio = '127.0.0.1:%s' % port_minio if local_minio else host_minio + ':' + port_minio
        secure_minio = True if minio_protocol == 'https' else False

        MINIO_PROTOCOL = minio_protocol
        MINIO_HOST = host_minio
        MINIO_PORT = port_minio
        MINIO_ENDPOINT = endpoint_minio
        MINIO_ACCESS_KEY = username_minio
        MINIO_SECRET_KEY = password_minio
        MINIO_SECURE = secure_minio
        MINIO_BUCKET = bucket_minio
    except:
        MINIO_PROTOCOL = None
        MINIO_HOST = None
        MINIO_BUCKET = None
        print('\nconfiguration of minio not found.')
        print('Run command: flask setoss\n')
        
    try:
        MAIL_SERVER = config['host_email']
        MAIL_PORT = config['port_email']
        MAIL_USE_SSL = config['ssl_email']
        MAIL_USE_TLS = config['tls_email']
        MAIL_USERNAME = config['address_email']
        MAIL_PASSWORD = config['password_email']
        MAIL_DEFAULT_SENDER = ('Blog Admin', MAIL_USERNAME)
        BLOG_EMAIL = config['receive_email']
    except:
        BLOG_EMAIL = None
        MAIL_SERVER = None
        MAIL_USERNAME = None
        MAIL_PASSWORD = None
        print('\nConfiguration of email not found.')
        print('Run command: flask setemail\n')
