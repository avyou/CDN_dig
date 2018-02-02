### 安装

#### dig工具的安装
脚本目前依赖于 dig 工具的EDNS功能支持，后续更新可能会放弃他而使用python 的pydig库。
```
wget ftp://ftp.isc.org/isc/bind9/9.9.3/bind-9.9.3.tar.gz
tar xf bind-9.9.3.tar.gz
cd bind-9.9.3

wget http://wilmer.gaa.st/edns-client-subnet/bind-9.9.3-dig-edns-client-subnet-iana.diff
patch -p0 < bind-9.9.3-dig-edns-client-subnet-iana.diff
./configure --prefix=/usr/local/dig   --without-openssl
make
```

### 安装 CDN_dig
```
git clone git@github.com:avyou/CDN_dig.git
cd CDN_dig
python setup.py install  
//如果以前由于一些依赖库安装不成功，可以先使用pip直接安装依赖，然后再重新执行一遍，如下：
pip install -r  requirements.txt
```
### 配置
配置和数据文件默认安装到: /usr/local/CDN_dig/，如果dig 安装的路径一致，默认配置是不用修改的，安装完即可使用。

####目录结构

```
tree
.
├── bin
│   ├── cdig        ##执行文件 ,PATH 路径同存在一份
│   └── whereip    ##执行文件 ,PATH 路径同存在一份
├── data
│   ├── ip_dns_isp.list   ## 全国DNS ip 列表文件，我自己整理的
│   ├── ipipdb.dat    ## IP 查询数据库，github上没有
│   └── qqwry.dat     ## 纯真IP 查询数据库
└── etc
    └── config.ini    ##配置文件 

	
```
当然还有安装到 python库目录的主要脚本文件，这里不写了。

####配置文件解析

```
cat /usr/local/CDN_dig/etc/config.ini 
[BASE]
default_api = ip138   ##默认接口
default_dns = 119.29.29.29    ##默认EDNS
ipdns_db = /usr/local/CDN_dig/data/ip_dns_isp.list  ##全国DNS的IP列表
tmp_dir = /tmp/dig    ##结果输出到文件和临时目录
dig = /usr/local/dig/bin/dig   ## dig 二进制文件路径

[API]
ip138 = http://www.ip138.com/ips138.asp?ip=   ##ip138 抓取的接口，不要抓得太多了^~^
#ipdb = /usr/local/CDN_dig/data/ipipdb.dat    ##ipip的收费IP查询数据库，没上传
chinaz = http://ip.chinaz.com/     ##chinaz 抓取的接口
qqwry = /usr/local/CDN_dig/data/qqwry.dat  ##纯真IP查询数据库,2018年1月份的
```








