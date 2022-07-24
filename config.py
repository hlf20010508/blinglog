# :project: bluelog
# :author: L-ING
# :copyright: (C) 2022 L-ING <hlf01@icloud.com>
# :license: MIT, see LICENSE for more details.

import json
import pymysql
from minio import Minio
from werkzeug.security import generate_password_hash


def init():
    username_blog = input('Username of blog: ')
    password_blog = input('Password of blog: ')

    host_minio = input(
        'Host name or ip address of minio server (eg: example.com:9000): ')
    secure_minio = True if input(
        'Protocol of server: 0 http 1 https ') == '1' else False
    local_minio = True if input(
        'Is minio in the same server with blog? 0 No 1 Yes ') == '1' else False
    username_minio = input('Username of minio: ')
    password_minio = input('Password of minio: ')
    bucket = input('Bucket name: ')

    host_mysql = input(
        'Host name or ip address of mysql server (eg: example.com:3306) : ')
    local_mysql = True if input(
        'Is mysql in the same server with blog? 0 No 1 Yes ') == '1' else False
    username_mysql = input('Username of mysql: ')
    password_mysql = input('Password of mysql: ')
    database = input('Database name: ')

    email_setted = True if input(
        'Use email for notification? 0 No 1 Yes ') == '1' else False

    config = {
        'username_blog': username_blog,
        'password_blog': password_blog,
        'host_minio': host_minio,
        'secure_minio': secure_minio,
        'local_minio': local_minio,
        'username_minio': username_minio,
        'password_minio': password_minio,
        'bucket': bucket,
        'host_mysql': host_mysql,
        'local_mysql': local_mysql,
        'username_mysql': username_mysql,
        'password_mysql': password_mysql,
        'database': database,
        'email_setted': email_setted
    }

    if email_setted:
        config['host_email'] = input('Host name or ip address of email server with smtp (eg: smtp.mail.me.com): ')
        config['port_email'] = int(input('Port of email server with smtp (eg: 587): '))
        config['ssl_email'] = True if input('Use SSL? 0 No 1 Yes ')=='1' else False
        config['tls_email'] = True if input('Use TLS? 0 No 1 Yes ')=='1' else False
        config['address_email'] = input('Email address: ')
        config['password_email'] = input('Password of email: ')

    config_file = open('config.json', 'w')
    json.dump(config, config_file)
    config_file.close()
    print('Configuration completed')

    print('Initializing minio...')
    init_minio(host_minio, username_minio, password_minio, bucket)

    print('Initializing mysql...')
    port = int(host_mysql.split(':')[1])
    host = '127.0.0.1' if local_mysql else host_mysql.split(':')[0]
    init_mysql(host, username_mysql,
               password_mysql, port, database, username_blog, password_blog)

    print('Initialization completed')

    # config=load()

    # print('Initializing minio...')
    # init_minio(config['host_minio'], config['username_minio'], config['password_minio'], config['bucket'])

    # print('Initializing mysql...')
    # port = int(config['host_mysql'].split(':')[1])
    # host = '127.0.0.1' if config['local_mysql'] else config['host_mysql'].split(':')[0]
    # init_mysql(host, config['username_mysql'],
    #            config['password_mysql'], port, config['database'], config['username_blog'], config['password_blog'])


def load():
    try:
        config_file = open('config.json', 'r')
    except:
        print('Configuration not found, run config.py first')
        print('python config.py')
        exit()
    config = json.load(config_file)
    config_file.close()
    return config


def init_minio(host, username, password, bucket):
    # create bucket if not exists
    client = Minio(
        host,
        access_key=username,
        secret_key=password,
        secure=False
    )
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
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
    client.set_bucket_policy(bucket, json.dumps(policy))


def init_mysql(host, user, password, port, database, user_blog, password_blog):
    # create database and table if not exists
    conn = pymysql.connect(host=host, user=user,
                           password=password, port=port, charset='utf8mb4', autocommit=True)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "create database if not exists %s" % database
    cursor.execute(sql)

    sql = "use %s" % database
    cursor.execute(sql)

    sql = '''create table if not exists admin(
    id bigint primary key auto_increment,
    username varchar(20) not null,
    password_hash varchar(128) not null,
    blog_title varchar(60),
    blog_sub_title varchar(100),
    name varchar(30),
    about longtext
    )
    '''
    cursor.execute(sql)

    password_hash_blog = generate_password_hash(password_blog)
    sql = '''select username from admin where username="%s"''' % user_blog
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result):
        sql = '''update admin set password_hash = "%s" where username = "%s"''' % (
            password_hash_blog, user_blog)
    else:
        blog_title = 'Bluelog',
        blog_sub_title = "No, I'm the real thing.",
        name = 'Admin',
        about = 'Anything about you.'
        sql = '''insert into admin(username, password_hash, blog_title, blog_sub_title, name, about) values("%s", "%s")''' % (
            user_blog, password_hash_blog, blog_title, blog_sub_title, name, about)
    cursor.execute(sql)

    sql = '''create table if not exists category(
    id bigint primary key auto_increment,
    name varchar(30) not null
    )
    '''
    cursor.execute(sql)

    sql = '''select name from category where name="Default"'''
    cursor.execute(sql)
    result = cursor.fetchall()
    if not len(result):
        sql = '''insert into category(name) values("%s")''' % ('Default')
        cursor.execute(sql)

    sql = '''create table if not exists comment(
    id bigint primary key auto_increment,
    author varchar(30),
    email varchar(254),
    site varchar(255),
    body longtext,
    from_admin tinyint,
    reviewed tinyint,
    timestamp datetime,
    replied_id bigint,
    post_id bigint
    )
    '''
    cursor.execute(sql)

    sql = '''create table if not exists link(
    id bigint primary key auto_increment,
    name varchar(30),
    url varchar(255)
    )
    '''
    cursor.execute(sql)

    sql = '''create table if not exists post(
    id bigint primary key auto_increment,
    title text,
    body longtext,
    timestamp datetime,
    can_comment tinyint,
    category_id bigint,
    img_name longtext
    )
    '''
    cursor.execute(sql)

    conn.close()


if __name__ == '__main__':
    init()
