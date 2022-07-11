```bash
# 安装pipenv
pip3 install pipenv

# 安装环境
pipenv sync

# 初始化配置文件
# minio和mysql都会自动初始化，且不会覆盖已有的数据
pipenv run python config.py

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
