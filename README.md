### 介绍
这是我入职快网后写的一个用于在linux 终端快速查询全国 CDN 域名调度到哪个区域节点的工具（部分自定的特性和IP查询数据库已从代码中去掉）。
工具类似下面命令的封装：

`dig @119.29.29.29 www.baidu.com  +client=218.203.160.194`


### 项目地址
https://github.com/avyou/CDN_dig

### 主要特性

- 支持电信、联通、移动、铁通、长宽、教育网等网络的域名调度查询；
- 利用 dig 的 EDNS 功能，能快速查询并输出结果，而不需要在全国各地部署节点；
- 支持输入多个运营商或多个省份别名的指定查询；
- 支持指定IP查询调度，支持更换EDNS；
- 支持更换IP查询接口, 查询失败轮询接口; 
- 支持输出CDN调度覆盖的统计结果；
- 支持多IP地址查询（whereip）；

### 用法
#### cdig 工具
		cdig -d <--domain> [-h <--help>] [-i,--ip>] [-a,--isp] [-n,--edns]

        参数：
              -d, --domain=: 后面跟要的查询域名，必选项.
              -h, --help:    帮助信息.
              -i, --ip=:     后面跟要查询的IP，可选，如果不填，且无 -a或--isp=选项 ，默认查看全网调度.
                             如果 --ip 与 --isp 同时指定，只取--ip.
              -a, --isp=:    区域别名，如ctl-gd，表示要查询客户端IP在广东电信访问时域名被调度的哪里.多个ISP用逗号分隔. --isp 的别名映射在 %s 文件.
              -n, --edns=:   使用指定的且支持EDNS的IP进行解析，可选，默认是 119.29.29.29
        举例：
              1). sudo cdig --domain=www.duowan.com --isp=cmb-sd           ##查询此域名山东移动被调度哪里
              2). sudo cdig --domain=www.duowan.com --isp=cmb-sd,cnc-sd    ##查询多个ISP用逗号分隔
              3). sudo cdig --domain=www.duowan.com --isp=cmb              ##查询此域名全部移动被调度哪里,查询多个ISP用逗号分隔
              4). sudo cdig --domain=www.duowan.com --isp=ctl,cnc          ##查询多个ISP用逗号分隔 
              5). sudo cdig --domain=www.duowan.com --ip=1.1.1.1           ##查询此域名在1.1.1.1被调度哪里
              6). sudo cdig --domain=www.duowan.com                        ##无--ip或--ISP选项，默认使用查询全网调度
              7). sudo cdig --domain=www.duowan.com --edns=8.8.8.8         ##指定其他EDNS如:8.8.8.8

##### 关于运营商及省份别名使用说明见文档最后<<附加说明>>部分			  
			  
#### whereip 工具
这个是模仿快网 “nali” 功能的工具，不过这个是我自己写的代码，用了另外的IP查询接口，加了对管道输入和文件输入的查询输出排版。

```
whereip  <ip|ip_file>

cmd |whereip
```

举例：

    1. whereip  202.117.112.3
	2. whereip  202.117.112.3  219.146.1.66 
	3. echo "202.117.112.3" |whereip
	4. whereip  ip.txt
	5. cat ip.txt |whereip
	

### 截图

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/cdn_dig_01.png)

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/cdn_dig_02.png)

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/cdn_dig_03.png)

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/cdn_dig_04.png)

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/whereip_01.png)

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/whereip_02.png)

![Alt text](https://github.com/avyou/CDN_dig/blob/master/document/img/whereip_03.png)

### 安装说明

https://github.com/avyou/CDN_dig/blob/master/document/INSTALL.md

### 附加说明

#### ISP简称对应表

```
CTL    电信
CNC    联通
CMB    移动
GWB    长宽
CRC    铁通
CER    教育网
```

#### 省份区域对应列表

```
BJ    北京
TJ    天津
HE    河北
SX    山西
NM    内蒙古
LN    辽宁
JL    吉林
HL    黑龙江
SH    上海
JS    江苏
ZJ    浙江
AH    安徽
FJ    福建
JX    江西
SD    山东
HA    河南
HB    湖北
HN    湖南
GD    广东
GX    广西
HI    海南
CQ    重庆
SC    四川
GZ    贵州
YN    云南
XZ    西藏
SN    陕西
GS    甘肃
QH    青海
NX    宁夏
XJ    新疆
HK    香港
MO    澳门
TW    台湾
CN    中国其它
JP    日本
KR    韩国
AP    亚太其它
OT    其余地区
```
























