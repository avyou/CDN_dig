### 介绍
这是我入职快网后写的一个用于在linux 终端快速查询全国 CDN 调度哪里区域节点的工具。
类似下面命令的封装：

dig @119.29.29.29 www.baidu.com  +client=218.203.160.194

因可能涉及隐私，有些自定的特性和IP查询数据库已从代码中去掉。

### 主要特性

- 支持电信、联通、移动、铁通、长宽、教育网调度的查询；
- 利用 dig 的 EDNS 功能，能快速得到查询结果,而不需要在全国部署节点；
- 支持输入多个运营商指定查询；
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
              8). sudo cdig --domain=otafs.coloros.com.cloudglb.com. --ip 113.9.222.69   ## 加后缀 cloudglb.com 进行解析指定域名

#### whereip 工具
这个是模仿快网 “nali” 的工具，但是我自己别写的代码，用了另外的IP查询接口，加了对管道输入和文件输入的查询输出排版。

whereip  ip

举例：

    1. whereip  202.117.112.3
	2. whereip  202.117.112.3  219.146.1.66 
	3. echo "202.117.112.3" |whereip
	4. whereip  ip.txt
	5. cat ip.txt |whereip
	

### 截图































