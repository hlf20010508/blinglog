安装pipenv
```
pip3 install pipenv
```
若没有增加环境变量，则执行
```
echo "export PATH=\"/home/ubuntu/.local/bin:$PATH\"" >> ~/.bashrc
source ~/.bashrc
```
安装环境
```
pipenv install
```
复制service文件
```
sudo cp blog@.service /usr/lib/systemd/system
```
开启服务
```
sudo systemctl start blog@ubuntu
```
开机自启
```
sudo systemctl enable blog@ubuntu
```