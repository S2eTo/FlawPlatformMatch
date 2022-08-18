# 一、软件运行环境和简介

功能定制，商务合作，问题/交流群: [512897146](https://jq.qq.com/?_wv=1027&k=V2mVBvL3)

特别说明, 本作品 前端[FlawPlatformMatchVue](https://github.com/S2eTo/FlawPlatformMatchVue), 后端[FlawPlatformMatch](https://github.com/S2eTo/FlawPlatformMatch)可开源使用，但必须免费提供使用。用于任何形式的商务/盈利活动，请提前联系交流群群主。

## 1.1 软件简介

基于 Docker, 使用 Python + Django 开发的在线 CTF 竞技平台。

支持在线答题、比赛管理、批量用户导入、动态 Flag、题目实时发布/下架题目、题目Hints(提示)发布/关闭提示、排行、动态、公告、积分等。题目分数为动态分数，做得人越多分越少(会影响之前已答手上的分数)。

目前是用本校于校内比赛，所以批量导入会有学号、班级等信息，excel(.xls) 列为：姓名、班级、学号。

# 二、安装说明

## 2.1 前端地址

项目为前后端分离项目，前端仓库：https://gitee.com/J0hNs0N/FlawPlatformMatchVue

## 2.2 安装 Python 3

安装依赖环境

```sh
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel gcc libffi-devel 
```

下载 python 3.7.1。若出现 command not found 的错误，通过命令 yum -y install wget 安装 wget 即可

```sh
wget https://www.python.org/ftp/python/3.7.1/Python-3.7.1.tgz
```

创建安装目录

```sh
mkdir -p /usr/local/python3
```

解压安装包

```sh
tar -zxvf Python-3.7.1.tgz
```

进入解压后的 Python 3 安装包目录

```sh
cd Python-3.7.1
```

生成编译脚本

```sh
./configure --prefix=/usr/local/python3
```

编译安装

```sh
make && make install
```

测试安装是否成功

```sh
/usr/local/python3/bin/python3
```

创建软连接

```sh
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
ln -s /usr/local/python3/bin/python3 /usr/bin/python3
```

安装所需依赖

```sh
yum install python-devel -y
yum install zlib-devel -y
yum install libjpeg-turbo-devel -y
```

## 2.3 使用 SQLite3 数据库

程序默认使用 SQLite3 数据库，但需要升级，若不想使用 SQLite3 可以直接跳转到下一章 **3. 使用Mysql 数据库**

### 2.3.1 升级 SQLite3

获取安装包下载地址：https://www.sqlite.org/download.html

![image-20220329121505366](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220329121505366.png)

下载 Sqlite 最新版安装包

```sh
wget https://www.sqlite.org/2022/sqlite-autoconf-3380200.tar.gz
```

解压安装包

```sh
tar zxvf sqlite-autoconf-3380200.tar.gz
```

进入解压后的安装包目录

```sh
cd sqlite-autoconf-3380200
```

生成编译脚本

```sh
./configure --prefix=/usr/local/sqlite3
```

编译安装

```sh
make && make install
```

检查安装是否成功

```sh
/usr/local/sqlite3/bin/sqlite3 --version
```

检查旧版本

```sh
/usr/bin/sqlite3 --version
```

将旧版本更换名字

```sh
mv /usr/bin/sqlite3  /usr/bin/sqlite3_old
```

设置新版本软连接

```sh
ln -s /usr/local/sqlite3/bin/sqlite3 /usr/bin/sqlite3
```

检查 *sqlite3* 版本

```sh
sqlite3 --version
```

编辑环境变量文件 `$HOME/.bash_profile` 添加下列变量

```
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/sqlite3/lib"
```

![image-20220408233636108](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220408233636108.png)

重新加载环境变量

```
source $HOME/.bash_profile
```

检查版本

![image-20220329123359686](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220329123359686.png)

### 2.3.2 迁移数据库

解压项目压缩文件后，cd 切换工作目录到项目文件夹中，与 `manage.py` 同级

![image-20220402231631573](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231631573.png)

创建迁移记录

```sh
pyhton3 manage.py makemigrations
```

迁移创建数据库

```sh
pyhton3 manage.py migrate
```

## 2.4. 使用 Mysql 数据库

### 2.4.1 安装 Mysql 数据库

centos 直接安装 mariadb 即可

```sh
yum -y install mariadb
```

### 2.4.2 修改程序配置文件

建议设置只在内网开放 3306 端口 通过 `bind-address` 设置（注意保存后重启服务）

```sh
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0
# Settings user and group are ignored when systemd is used.
# If you need to run mysqld under a different user or group,
# customize your systemd unit file for mariadb according to the
# instructions in http://fedoraproject.org/wiki/Systemd

# 设置绑定的 IP 地址为环回口地址 127.0.0.1
bind-address=127.0.0.1

[mysqld_safe]
log-error=/var/log/mariadb/mariadb.log
pid-file=/var/run/mariadb/mariadb.pid

#
# include all files from the config directory
#
!includedir /etc/my.cnf.d
```

重启服务

```sh
systemctl restart mariadb
```

检查端口绑定情况

![image-20220329152729950](D:\广东省大学生计算机设计大赛\说明文档\信息安全竞技平台\image-20220329152729950-16488048778422.png)

### 2.4.3 设置 Mysql 密码

为了安全考虑，哪怕只开在回环口也需要设置登录密码。如果觉得不需要设置，可以跳过这一步

默认密码是空的，可以直接通过 `mysql -u root -p` 空密码登录即可

![image-20220329152835883](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220329152835883.png)

这里通过直接更新数据表的方式修改密码

```mysql
UPDATE user SET Password = PASSWORD('密码') WHERE user = 'root';
```

刷新

```mysql
FLUSH PRIVILEGES;
```

### 2.4.4 创建数据库

为程序创建一个数据库，名字自定义。但后面配置 Django 时需要填对

```
flaw_platform
```

![image-20220329160204619](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220329160204619.png)

### 2.4.5 配置编码

编辑 `/etc/my.conf` ，设置 编码。记得重启 mariadb 服务

```sh
[client]
# 设置编码
default-character-set=utf8

[mysql]
# 设置编码
default-character-set=utf8

[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0
# Settings user and group are ignored when systemd is used.
# If you need to run mysqld under a different user or group,
# customize your systemd unit file for mariadb according to the
# instructions in http://fedoraproject.org/wiki/Systemd

# 设置绑定地址
bind-address=127.0.0.1


# 设置编码
collation-server=utf8_unicode_ci
init-connect='SET NAMES utf8'
character-set-server=utf8


[mysqld_safe]
log-error=/var/log/mariadb/mariadb.log
pid-file=/var/run/mariadb/mariadb.pid

#
# include all files from the config directory
#
!includedir /etc/my.cnf.d
```

### 2.4.6 配置 Django 使用 Mysql 数据库

解压项目压缩文件后，cd 切换工作目录到项目文件夹中，与 `manage.py` 同级

![image-20220402231623965](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231623965.png)

安装 mysqlclient

```sh
pip3 install mysqlclient
```

出现报错以下两种方法解决

```
# 更新pip
pip3 install --upgrade pip

# 安装 mysql-devel
yum install mysql-devel
```

编辑 `common/settings.py` 文件

```sh
vim common/settings.py
```

进行如下修改, 注意保存

```sh
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',

        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': '',                             # 数据库名，先前创建的
        'USER': 'root',                         # 用户名，可以自己创建用户
        'PASSWORD': 'xxxx',                     # 密码
        'HOST': '127.0.0.1',                    # mysql服务所在的主机ip
        'PORT': '3306',                         # mysql服务端口
    }
}
```

创建迁移记录

```sh
pyhton3 manage.py makemigrations
```

![image-20220402231618940](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231618940.png)

迁移创建数据库

```sh
pyhton3 manage.py migrate
```

## 2.5. 配置 Docker

### 2.5.1 安装 docker

通过 yum 一键安装即可

```sh
yum -y install docker
```

### 2.5.2 配置 Remote API

编辑服务配置文件

```sh
vim /usr/lib/systemd/system/docker.service
```

再  ExecStart 值中添加多一行，**注: 这里最好不要暴露在公网上，因为这里的 Remote API 没有身份校验。任何人都可以通过这个 Remote API 操作你的 Docker，进行操作。**

```
-H tcp://127.0.0.1:2375 -H unix:///var/run/docker.sock
```

![image-20220329104619088](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220329104619088.png)

重启 Docker 服务

```sh
systemctl daemon-reload
systemctl restart docker
```

检查端口是否开启，如果 `netstat command not found` 需要安装 *net-tools* : `yum -y install net-tools` 

```
netstat -ano | grep 2375
```

![image-20220329104535343](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220329104535343.png)

### 2.5.3 配置 Django Docker Remote API 信息

cd 切换工作目录到项目文件夹中，与 `manage.py` 同级

![image-20220402231609883](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231609883.png)

编辑 `common/settings.py` 文件

```sh
vim common/settings.py
```

进行如下修改, 注意保存

```python
DOCKER_API = {
    'URL': 'tcp://127.0.0.1:2375',
    
    # 外部映射地址, 只起到显示作用。同时是提供外部访问容器端口的地址
    'EXTERNAL_URL': '10.8.7.46',
    
    # 映射端口区间如：30000-30500, 设置为 None 表示不设限制区间
    'PUBLIC_PORT_RANG': None,
    
    # 随机 Flag 设置的环境变量名称，建议默认
    'FLAG_ENVIRONMENT_NAME': 'RANDOM_FLAG',
    
    # 自动删除容器/靶机时间如: +1 为一小时后自动关闭
    'AUTO_REMOVE_CONTAINER': +1
}
```

## 2.6. 部署后端

### 2.6.1 安装所需包

cd 切换工作目录到项目文件夹中，与 `manage.py` 同级

![image-20220402231553787](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231553787.png)

使用 *pip* 安装 *requirements.txt* 

```
pip3 install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
```

### 2.6.2 启动服务

cd 切换工作目录到项目文件夹中，与 `manage.py` 同级

![image-20220402231551118](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231551118.png)

启动服务

```sh
# python3 manage.py runserver IP:PORT
python3 manage.py runserver 10.8.7.46:8000
```

![image-20220402231825845](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402231825845.png)

### 2.6.3 管理后台

通过 `createsuperuser` 创建超级管理员用户

```
python3 manage.py createsuperuser
```

即可通过创建的用户民密码登录后台：`http://ip:port/admin/`

![image-20220402232104258](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402232104258.png)

![image-20220402232138409](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220402232138409.png)

# 三、管理员使用说明

访问站点管理页面：http://xn.gdcp.edu.cn:8001/admin/ (连接为`[host/ip]/admin/`)，输入用户名密码登录即可。

![image-20220406151913946](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406151913946.png)

需要管理时，选择点击左边模块即可。

![image-20220406152151832](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406152151832.png)

## 3.1 选手信息导入

导入需要特定的 excel 文件，与《信息安全管理与评估》赛项同样的三人一队设计

```
队伍名称、队员1姓名(队长)、队员1班级、队员1学号、队员2姓名、队员2班级、队员2学号、队员3姓名、队员3班级、队员3学号。
```

如下是示例。*表中设计的名称、姓名均通过随机姓名生成网站生成，如有雷同纯属巧合*

![image-20220406150335317](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406150335317.png)

### 3.1.1 选手信息收集

这里演示通过微信小程序《金山文档》来收集参赛队伍信息，创建好规定模板文档

![image-20220406150853186](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406150853186.png)

点击右上角分享按钮，选择任何人可编辑，点击创建并分享

![image-20220406150928630](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406150928630.png)

可以复制连接发送，也可以通过生成二维码的方式要去他人加入分享编辑。

![image-20220406151211757](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406151211757.png)

将连接或二维码发送提供参赛选手填写队伍信息即可。

![image-20220406151320198](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406151320198.png)

### 3.1.2 导出选手信息

点击左上角选择导出为 Excel(.xls) 即可

![image-20220406151630061](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406151630061.png)

### 3.1.3 选手信息导入

进入用户管理界面，点击右上角批量导入用户信息

![image-20220406152240729](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406152240729.png)

选择收集好的选手信息文件，点击执行导入即可。程序会自动判断队伍名称、选手是否重复，导入信息时间会很长，请耐心等待直到提示导入完成为止。导入成功后会自动创建队伍、用户并自动关联。**登录用户名(账号)为学号、密码默认 123456 **

![image-20220406152347711](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406152347711.png)

## 3.2 用户(选手)管理

特别说明：管理员或裁判用户必须加入到名为：裁判组 的队伍中，否则无法访问态势/倒计时页面

### 3.2.1 编辑用户

在列表页选择点击用户名一栏即可进入编辑页面

![image-20220406154324135](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406154324135.png)

在比赛中基本对选手做个人信息编辑即可，可以调整名字，队伍，积分等。

![image-20220406154405455](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406154405455.png)

页面底部可以选择：删除、保存等操作

![image-20220406154519551](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406154519551.png)

### 3.2.2 用户搜索

可以通过用户名（学号）、姓名、邮箱进行搜索，点击搜索按钮右侧的 `总共 ..` 可以返回所有列表页。

![image-20220406154746552](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406154746552.png)

### 3.2.3 手动添加用户(选手)

在用户列表页，点击右上角增加用户，进入添加用户页面

![image-20220406154931184](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406154931184.png)

输入用户名、密码、确认密码后点击保存即可。

![image-20220406155016960](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155016960.png)

### 3.3.4 批量删除用户(选手)

选择需要批量删除的队伍，选择删除所选队伍的动作，点击执行

![image-20220406160725455](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406160725455.png)

在确认页面点击确认即可

![image-20220406160825576](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406160825576.png)

## 3.3 队伍管理

特别说明：管理员或裁判用户必须加入到名为：裁判组 的队伍中，否则无法访问态势/倒计时页面

### 3.3.1 编辑队伍

进入队伍列表后，选择点击名称一列即可进入编辑页面

![image-20220406155238311](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155238311.png)

选择修改队伍名称或分数，点击保存即可

![image-20220406155417504](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155417504.png)

也可以点击左下角的删除按钮单独删除队伍

![image-20220406155519601](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155519601.png)

删除队伍会同步删除队伍成员

![image-20220406155538816](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155538816.png)

### 3.3.2 搜索

可以根据名称搜索队伍，点击搜索按钮右侧的 `总共 ..` 可以返回所有列表页。

![image-20220406155637512](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155637512.png)

### 3.3.3 手动添加队伍

点击右上角增加队伍进入添加队伍页面

![image-20220406160552232](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406160552232.png)

输入用户名点击保存即可

![image-20220406160632664](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406160632664.png)

### 3.3.4 批量删除队伍

选择队伍，选择删除所选队伍的动作，点击执行

![image-20220406155748607](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406155748607.png)

在确认页面点击确认即可

![image-20220406160140311](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406160140311.png)

## 3.4 比赛管理

这里有两种使用方法：添加一个比赛后，再次举办比赛时修改改信息就行。或每次举办比赛时添加一个比赛，程序会自动将最新记录作为当前比赛信息。

### 3.4.1 添加比赛

点击右上角增加比赛，

![image-20220406182902535](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406182902535.png)

填写好比赛名称、logo、开始时间、结束时间点击保存即可。

![image-20220406183722319](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406183722319.png)

logo和名称的效果位于页面左上角，比赛开始/结束时间用于比赛倒计时，及比赛信息。下面是态势页面，当然不仅态势页面。

![image-20220406183828154](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406183828154.png)

### 3.4.2 编辑比赛信息

在比赛管理列表页，点击比赛名称列可进入编辑页面

![image-20220406224202627](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224202627.png)

完成编辑后点击右下角保存即可

![image-20220406224235244](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224235244.png)

### 3.4.3 搜索

在列表页可以通过赛名称进行搜索

![image-20220406224336134](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224336134.png)

## 3.5 分类管理

可以删除、批量删除、编辑、搜索、添加、过滤、排序分类，与文档前面的内容过于相似这里不再演示。

![image-20220406233513838](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406233513838.png)

## 3.6 题目管理

可以删除、批量删除、编辑、搜索、添加、过滤、排序题目，与文档前面的内容过于相似这里不再演示

### 3.6.1 镜像环境 - 环境变量随机flag

在列表页点击右上角 *增加题目* 按钮

![image-20220406224835640](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224835640.png)

题目环境选择镜像环境，填入镜像 ID （这里需要本地的docker中存在该镜像）程序会自动根据 镜像ID 获取镜像标签与开发端口信息。镜像Flag形式选择环境变量随机flag

![image-20220406224921485](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224921485.png)

这样的环境本质上就是在容器环境变量中设置一个 `RANDOM_FLAG`（可更改） 的环境变量值就是随机生成的 flag，通过PHP等程序可以获取该变量

```php
<?php
echo(getenv('RANDOM_FLAG'));
```

填写完成基本信息后点击保存即可

![image-20220406225119013](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406225119013.png)

### 3.6.2 镜像环境 - 本地文件随机flag

在列表页点击右上角 *增加题目* 按钮

![image-20220406224835640](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224835640.png)

题目环境选择镜像环境，填入镜像 ID （这里需要本地的docker中存在该镜像）程序会自动根据 镜像ID 获取镜像标签与开发端口信息。镜像FLAG样式选择 本地文件随机flag, 填写文件路径、文件内容模板，填写完基本信息即可

![image-20220406225638522](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406225638522.png)

如下是题目效果

![image-20220406225756827](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406225756827.png)

### 3.6.3 附件环境

在列表页点击右上角 *增加题目* 按钮

![image-20220406224835640](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406224835640.png)

将题目环境切换为附件环境，选择附件，设置附件flag，填写完题目信息即可

![image-20220406225914236](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406225914236.png)

### 3.6.4 实时发布题目

添加完题目后，选手是看不到题目的，只有 **在比赛开始后** 在题目列表中点击上架题目

![image-20220406230110083](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406230110083.png)

进入确认页面后点击确认即可，题目会实时推送上架，并实时推送公告。

![image-20220406230222449](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406230222449.png)

如下公告

![image-20220406230354977](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406230354977.png)

选手端小公告效果

![image-20220406232044028](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406232044028.png)

### 3.6.5 紧急下架题目

在列表页点击下架题目

![image-20220406232640950](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406232640950.png)

紧急下架题目后会自动关闭与题目相关的所有容器，这可能会非常耗费资源，谨慎使用。

![image-20220406232700685](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406232700685.png)

### 3.6.6 题目搜索

在列表页可以根据 题目名称、题目来源、题目描述、镜像 ID 进行搜搜

![image-20220406233129959](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406233129959.png)

## 3.7 靶机(容器)管理

添加靶机(容器)时选择响应题目，点击保存可以生成一个环境

![image-20220406233606469](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406233606469.png)

添加成功

![image-20220406233645933](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406233645933.png)

## 3.8 比赛态势

特别说明：管理员或裁判用户必须加入到名为：裁判组 的队伍中，否则无法访问态势/倒计时页面

![image-20220406233948227](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406233948227.png)

裁判组用户/管理员，可直接访问站点主页：http://xn.gdcp.edu.cn:8001/ (`http://ip/host:port/`) 会自动跳转到态势页面，登录后台后可以通过点击右上角的查看站点跳转到态势页面

![image-20220406234039216](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406234039216.png)

态势页面连接：http://xn.gdcp.edu.cn:8001/#/twinkingstar（`http://ip:port/#/twinkingstar`），

![image-20220406234232706](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406234232706.png)

## 3.9 大屏幕倒计时

特别说明：管理员或裁判用户必须加入到名为：裁判组 的队伍中，否则无法访问态势/倒计时页面

访问连接：http://xn.gdcp.edu.cn:8001/#/countdown (`http://ip:port/#/countdown`)

![image-20220406234508400](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220406234508400.png)

# 四、选手使用说明

设有(每道题)前三作答额外奖励机制，第一额外奖励 20%，第二额外奖励 15%，第三额外奖励 10%.

## 4.1 登录

用户名(账号)为学号，密码默认 123456，输入验证码即可登录

![image-20220407000053598](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407000053598.png)

## 4.2 退出登录

登录后可通过右上角 退出登录 按钮退出当前账号

![image-20220407000354840](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407000354840.png)

## 4.3 切换分类

可以同点击相应分类切换题目列表

![image-20220407000629099](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407000629099.png)

## 4.4 镜像环境题目作答

点击相应题目

![image-20220407000856016](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407000856016.png)

点击启动环境

![image-20220407001024005](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001024005.png)

启动成功后，回给出环境连接。

![image-20220407001047336](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001047336.png)

复制连接访问作答即可

![image-20220407001200664](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001200664.png)

获取到 flag (答案) 后

![image-20220407001228357](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001228357.png)

将答案提交即可

![image-20220407001302876](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001302876.png)

作答完成效果

![image-20220407001323816](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001323816.png)

## 4.5 其他

动态、公告排行榜会实时推送更新。

![image-20220407001535962](https://gitee.com/J0hNs0N/read-me-images/raw/master/%E4%BF%A1%E6%81%AF%E5%AE%89%E5%85%A8%E7%AB%9E%E6%8A%80%E5%B9%B3%E5%8F%B0.assets/image-20220407001535962.png)
