# blinglog
> A blog engine built with Flask.

## 声明
- 本项目基于greyli的[bluelog](https://github.com/greyli/bluelog)

## 新功能
- 使用minio作为对象存储
- 使用mysql作为数据库
- 使用Markdown编辑器
- 取消评论审核
- 实现搜索功能，支持文章、标题、评论
- 自动清理无用图片
- 适配WebApp
- 优化邮件通知消息格式
- 评论管理和邮件通知可以定位到目标评论
- 可以使用docker部署
- 支持私有导航

## docker部署
### 若未初始化过Mysql和MinIO，需要先初始化
先前往 [直接运行](#direct_launch) 参考初始化命令来进行初始化

### 若已初始化过MySql和MinIO，调试时可以直接使用.env文件导入环境
创建配置文件
```sh
vim .env
```

输入配置（例子）
```sh
# mysql 服务器地址
host_mysql=123.123.123.123:3306
# mysql 用户名
username_mysql=root
# mysql 密码
password_mysql=12345678
# mysql 数据库名
database_mysql=blog
# minio 服务器地址
host_minio=https://123.123.123.123:9000
# minio 用户名
username_minio=user
# minio 密码
password_minio=12345678
# minio bucket名
bucket_minio=blog

# 通知邮箱设置（可省略）
# smtp服务器地址
host_email=smtp.mail.me.com
# smtp服务器端口号
port_email=587
# 是否使用ssl
ssl_email=false
# 是否使用tls
tls_email=true
# smtp邮箱用户名
address_email=user@icloud.com
# smtp邮箱密码
password_email=abcd-abcd-abcd-abcd
# 通知收件邮箱地址
receive_email=user@icloud.com
```

安装
```sh
# 安装docker-compose
pip install docker-compose
# 部署
docker-compose up -d
```

## docker构建
```sh
docker-compose -f docker-compose-build.yml up
```

<span id="direct_launch"></span>
## 直接运行
```bash
# 安装pipenv
pip3 install pipenv

# 安装环境
pipenv sync

# 初始化配置
# minio和mysql都会自动初始化，且不会覆盖已有的数据
pipenv run flask init

# 若不想初始化email，可用以下命令选择性初始化

# 仅初始化mysql
pipenv run flask setdb # 写入配置文件
pipenv run flask initdb # 执行初始化

# 仅初始化minio
pipenv run flask setoss # 写入配置文件
pipenv run flask initoss # 执行初始化

# 仅初始化blog
pipenv run flask initblog

# 仅配置email
pipenv run flask setemail

# 更改mysql配置
pipenv run flask changedb
'''
--host     [域名或IP地址]
--username [用户名]
--password [密码]
--database [数据库]
'''

# 更改minio配置
pipenv run flask changeoss
'''
--host     [域名或IP地址]
--username [用户名]
--password [密码]
--bucket   [桶]
'''

# 更改email配置
pipenv run flask changeemail
'''
--host     [SMTP服务器域名或IP地址]
--port     [端口号]
--ssl      [使用SSL y/n]
--tls      [使用TLS y/n]
--address  [邮箱地址]
--password [邮箱密码]
--receive  [通知收件地址]
'''

# 清空当前数据库
pipenv run flask initdb --drop

# 生成随机数据
pipenv run flask forge

# 查看命令
pipenv run flask --help

# 运行
pipenv run flask run -p 8080 -h 0.0.0.0

# 以下为设置开机自启和后台运行的方法
# 编辑blog@.service文件，参照已有命令更改第6行ExecStart和第11行WorkingDirectory

# 复制service文件
sudo cp blog@.service /usr/lib/systemd/system

# 启动服务 USERNAME是本机用户名，下同
sudo systemctl start blog@USERNAME

# 查看状态
sudo systemctl status blog@USERNAME

# 开机自启
sudo systemctl enable blog@USERNAME

# 重启服务
sudo systemctl restart blog@USERNAME

# 关闭服务
sudo systemctl stop blog@USERNAME

# 取消开机自启
sudo systemctl disable blog@USERNAME
```

## 相关链接
[Docker](https://hub.docker.com/repository/docker/hlf01/blinglog/general)
