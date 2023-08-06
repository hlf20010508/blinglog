# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError
from blog.settings import Config
from blog.blueprints.admin import admin_bp
from blog.blueprints.auth import auth_bp
from blog.blueprints.blog import blog_bp
from blog.extensions import bootstrap, db, login_manager, csrf, mail, moment, toolbar, migrate, minio
from blog.models import Admin, Post, Category, Comment, Link
import json
from sqlalchemy_utils import database_exists, create_database

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app():
    app = Flask('blog')
    app.debug = False
    app.config.from_object(Config)

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)
    register_shell_context(app)
    register_template_context(app)
    register_request_handlers(app)
    return app


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/blog.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject='Blog Application Error',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)
    minio.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        navigator = [link for link in links if link.is_navigator]
        public_links = [link for link in links if not link.is_navigator]
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin, categories=categories,
            links=links, navigator=navigator, public_links=public_links, unread_comments=unread_comments)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--host', prompt='The host name or IP address of smtp email server (eg: smtp.mail.me.com)', help='The host name or IP address of smtp email server (eg: smtp.mail.me.com).')
    @click.option('--port', prompt='The port of smtp email server (eg: 587)', type=int, help='The port of smtp email server (eg: 587).')
    @click.option('--ssl', prompt='Use SSL? y/n', type=click.BOOL, help='Whether to use SSL.')
    @click.option('--tls', prompt='Use TLS? y/n', type=click.BOOL, help='Whether to use TLS.')
    @click.option('--address', prompt='The email address on smtp server', help='The email address on smtp server.')
    @click.option('--password', prompt='The password of smtp email server', help='The password of smtp email server.')
    @click.option('--receive', prompt='The email address to receive notification', help='The email address to receive notification.')
    def setemail(host, port, ssl, tls, address, password, receive):
        """Set up configuration for email"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
        except:
            config = {}

        config['host_email'] = host
        config['port_email'] = port
        config['ssl_email'] = ssl
        config['tls_email'] = tls
        config['address_email'] = address
        config['password_email'] = password
        config['receive_email'] = receive

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        click.echo('Configuration of email set.')

    @app.cli.command()
    @click.option('--host', help='The host name or IP address of smtp email server (eg: smtp.mail.me.com).')
    @click.option('--port', type=int, help='The port of smtp email server (eg: 587).')
    @click.option('--ssl', type=click.BOOL, help='Whether to use SSL.')
    @click.option('--tls', type=click.BOOL, help='Whether to use TLS.')
    @click.option('--address', help='The email address on smtp server.')
    @click.option('--password', help='The password of smtp email server.')
    @click.option('--receive', help='The email address to receive notification.')
    def changeemail(host, port, ssl, tls, address, password, receive):
        """Change configuration of email"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            if host:
                config['host_email'] = host
            if port:
                config['port_email'] = port
            if ssl:
                config['ssl_email'] = ssl
            if tls:
                config['tls_email'] = tls
            if address:
                config['address_email'] = address
            if password:
                config['password_email'] = password
            if receive:
                config['receive_email'] = receive

            with open('config.json', 'w') as config_file:
                json.dump(config, config_file)
        except:
            pass

    @app.cli.command()
    @click.option('--host', prompt='The host name or IP address of mysql server (eg: example.com)', help='The host name or IP address of mysql server (eg: example.com).')
    @click.option('--port', prompt='The port of mysql server (eg: 3306)', help='The port of mysql server (eg: 3306).')
    @click.option('--username', prompt='The username of mysql server', help='The username of mysql server.')
    @click.option('--password', prompt='The password of mysql server', help='The password of mysql server.')
    @click.option('--database', prompt='The database name of mysql server', help='The database name of mysql server.')
    def setdb(host, port, username, password, database):
        """Set up configuration for mysql"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
        except:
            config = {}

        config['host_mysql'] = host
        config['port_mysql'] = port
        config['username_mysql'] = username
        config['password_mysql'] = password
        config['database_mysql'] = database

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        click.echo('Configuration of mysql set.')
        click.echo('Run command to initialize: flask initdb')

    @app.cli.command()
    @click.option('--host', help='The host name or IP address of mysql server (eg: example.com).')
    @click.option('--port', help='The port of mysql server (eg: 3306).')
    @click.option('--username', help='The username of mysql server.')
    @click.option('--password', help='The password of mysql server.')
    @click.option('--database', help='The database name of mysql server.')
    def changedb(host, port, username, password, database):
        """Change configuration of mysql"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            if host:
                config['host_mysql'] = host
            if port:
                config['port_mysql'] = port
            if username:
                config['username_mysql'] = username
            if password:
                config['password_mysql'] = password
            if database:
                config['database_mysql'] = database

            with open('config.json', 'w') as config_file:
                json.dump(config, config_file)
        except:
            pass

    @app.cli.command()
    @click.option('--host', prompt='The host name or IP address of minio server (eg: example.com)', help='The host name or IP address of minio server (eg: example.com).')
    @click.option('--port', prompt='The port of minio server (eg: 9000)', help='The port of minio server (eg: 9000).')
    @click.option('--protocol', prompt='The protocol type of minio server', type=click.Choice(['http', 'https']), help='The protocol type of minio server (http https).')
    @click.option('--local', prompt='Is minio on the same server with blog? y/n', type=click.BOOL, help='Whether minio is on the same server with blog.')
    @click.option('--username', prompt='The username of minio server', help='The username of minio server.')
    @click.option('--password', prompt='The password of minio server', help='The password of minio server.')
    @click.option('--bucket', prompt='The bucket name', help='The bucket name.')
    def setoss(host, port, protocol, local, username, password, bucket):
        """Set up configuration for minio"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
        except:
            config = {}

        config['host_minio'] = host
        config['port_minio'] = port
        config['protocol_minio'] = protocol
        config['local_minio'] = local
        config['username_minio'] = username
        config['password_minio'] = password
        config['bucket_minio'] = bucket

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        click.echo('Configuration of minio set.')
        click.echo('Run command to initialize: flask initoss')

    @app.cli.command()
    @click.option('--host', help='The host name or IP address of minio server (eg: example.com).')
    @click.option('--port', help='The port of minio server (eg: 9000).')
    @click.option('--protocol', type=click.Choice(['http', 'https']), help='The protocol type of minio server (http https).')
    @click.option('--local', type=click.BOOL, help='Whether minio is on the same server with blog.')
    @click.option('--username', help='The username of minio server.')
    @click.option('--password', help='The password of minio server.')
    @click.option('--bucket', help='The bucket name.')
    def changeoss(host, port, protocol, local, username, password, bucket):
        """Change configuration of minio"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)

            if host:
                config['host_minio'] = host
            if port:
                config['port_minio'] = port
            if protocol:
                config['protocol_minio'] = protocol
            if local:
                config['local_minio'] = local
            if username:
                config['username_minio'] = username
            if password:
                config['password_minio'] = password
            if bucket:
                config['bucket_minio'] = bucket

            with open('config.json', 'w') as config_file:
                json.dump(config, config_file)
        except:
            pass

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize mysql."""
        engine = db.create_engine(
            app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_ENGINE_OPTIONS'])
        if not database_exists(engine.url):
            create_database(engine.url)
        else:
            click.echo('Database already exists')
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized mysql.')

    @app.cli.command()
    def initoss():
        """Initialize minio."""
        bucket = app.config['MINIO_BUCKET']
        if not minio.bucket_exists(bucket):
            minio.make_bucket(bucket)
        else:
            print('Bucket "%s" already exists' % bucket)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                    ],
                    "Resource": "arn:aws:s3:::%s" % bucket,
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListMultipartUploadParts",
                        "s3:AbortMultipartUpload",
                    ],
                    "Resource": "arn:aws:s3:::%s/*" % bucket,
                },
            ],
        }
        minio.set_bucket_policy(bucket, json.dumps(policy))
        click.echo('Initialized minio.')

    @app.cli.command()
    @click.option('--username', prompt='The usename of blog', help='The usename of blog.')
    @click.option('--password', prompt='The password of blog', help='The password of blog.')
    def initblog(username, password):
        """Initialize blog"""

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Blog',
                blog_sub_title="No, I'm the real thing.",
                name=username,
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--username-blog', prompt='The usename of blog', help='The usename of blog.')
    @click.option('--password-blog', prompt='The password of blog', help='The password of blog.')
    @click.option('--host-mysql', prompt='The host name or IP address of mysql server (eg: example.com)', help='The host name or IP address of mysql server (eg: example.com).')
    @click.option('--port-mysql', prompt='The port of mysql server (eg: 3306)', help='The port of mysql server (eg: 3306).')
    @click.option('--username-mysql', prompt='The username of mysql server', help='The username of mysql server.')
    @click.option('--password-mysql', prompt='The password of mysql server', help='The password of mysql server.')
    @click.option('--database-mysql', prompt='The database name of mysql server', help='The database name of mysql server.')
    @click.option('--host-minio', prompt='The host name or IP address of minio server (eg: example.com)', help='The host name or IP address of minio server (eg: example.com).')
    @click.option('--port-minio', prompt='The port of minio server (eg: 9000)', help='The port of minio server (eg: 9000).')
    @click.option('--protocol-minio', prompt='The protocol type of minio server', type=click.Choice(['http', 'https']), help='The protocol type of minio server (http https).')
    @click.option('--local-minio', prompt='Is minio on the same server with blog? y/n', type=click.BOOL, help='Whether minio is on the same server with blog.')
    @click.option('--username-minio', prompt='The username of minio server', help='The username of minio server.')
    @click.option('--password-minio', prompt='The password of minio server', help='The password of minio server.')
    @click.option('--bucket-minio', prompt='The bucket name', help='The bucket name.')
    @click.option('--host-email', prompt='The host name or IP address of smtp email server (eg: smtp.mail.me.com)', help='The host name or IP address of smtp email server (eg: smtp.mail.me.com).')
    @click.option('--port-email', prompt='The port of smtp email server (eg: 587)', type=int, help='The port of smtp email server (eg: 587).')
    @click.option('--ssl-email', prompt='Use SSL? y/n', type=click.BOOL, help='Whether to use SSL.')
    @click.option('--tls-email', prompt='Use TLS? y/n', type=click.BOOL, help='Whether to use TLS.')
    @click.option('--address-email', prompt='The email address on smtp server', help='The email address on smtp server.')
    @click.option('--password-email', prompt='The password of smtp email server', help='The password of smtp email server.')
    @click.option('--receive-email', prompt='The email address to receive notification', help='The email address to receive notification.')
    def init(username_blog, password_blog, host_mysql, port_mysql, username_mysql, password_mysql, database_mysql,
                host_minio, port_minio, protocol_minio, local_minio, username_minio, password_minio, bucket_minio,
                host_email, port_email, ssl_email, tls_email, address_email, password_email, receive_email):
        """Initialize all"""
        config = {
            'host_mysql': host_mysql,
            'port_mysql': port_mysql,
            'username_mysql': username_mysql,
            'password_mysql': password_mysql,
            'database_mysql': database_mysql,
            'host_minio': host_minio,
            'port_minio': port_minio,
            'protocol_minio': protocol_minio,
            'local_minio': local_minio,
            'username_minio': username_minio,
            'password_minio': password_minio,
            'bucket_minio': bucket_minio,
            'host_email': host_email,
            'port_email': port_email,
            'ssl_email': ssl_email,
            'tls_email': tls_email,
            'address_email': address_email,
            'password_email': password_email,
            'receive_email': receive_email,
        }

        click.echo('Configuration saved.')

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)

        """Set up configuration for mysql"""
        engine = db.create_engine(
            app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_ENGINE_OPTIONS'])
        if not database_exists(engine.url):
            create_database(engine.url)
        else:
            click.echo('Database %s already exists'%database_mysql)
        db.create_all()
        click.echo('Initialized mysql.')

        """Set up configuration for minio"""
        bucket = app.config['MINIO_BUCKET']
        if not minio.bucket_exists(bucket):
            minio.make_bucket(bucket)
        else:
            click.echo('Bucket "%s" already exists' % bucket)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                    ],
                    "Resource": "arn:aws:s3:::%s" % bucket,
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListMultipartUploadParts",
                        "s3:AbortMultipartUpload",
                    ],
                    "Resource": "arn:aws:s3:::%s/*" % bucket,
                },
            ],
        }
        minio.set_bucket_policy(bucket, json.dumps(policy))
        click.echo('Initialized minio.')

        """Initialize blog"""
        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username_blog
            admin.set_password(password_blog)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username_blog,
                blog_title='Blog',
                blog_sub_title="No, I'm the real thing.",
                name=username_blog,
                about='Anything about you.'
            )
            admin.set_password(password_blog)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generate fake data."""
        from blog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        engine = db.create_engine(
            app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_ENGINE_OPTIONS'])
        if not database_exists(engine.url):
            create_database(engine.url)
        else:
            click.echo('Database already exists')
            db.drop_all()

        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')


def register_request_handlers(app):
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['SQLALCHEMY_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Context: %s\nQuery: %s\n '
                    % (q.duration, q.context, q.statement)
                )
        return response
