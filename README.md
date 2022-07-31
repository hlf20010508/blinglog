# blinglog
> A blog engine built with Flask.

## 声明
- 本项目基于greyli的[blulog](https://github.com/greyli/bluelog)

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

## 安装
```bash
# 安装pipenv
pip3 install pipenv

# 安装环境
pipenv sync

# 初始化配置文件
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
--port     [端口号]
--username [用户名]
--password [密码]
--database [数据库]
'''

# 更改minio配置
pipenv run flask changeoss
'''
--host     [域名或IP地址]
--port     [端口号]
--protocol [协议 http/https]
--local    [与博客同服务器 y/n]
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
