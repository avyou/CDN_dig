#!/usr/bin/env python
#-*- coding: utf-8 -*-
# EDNS dig is used to query where the client IP of request is dispatched for CDN
# by avyou
# at 20171019
# last update 20180201

import os
import sys
import re
import urllib2
import simplejson as json
import requests, re
from prettytable import PrettyTable
import getopt
from termcolor import colored
from tqdm import tqdm
from  models.queryIP import QueryIP

reload(sys)
sys.setdefaultencoding("utf-8")


ext = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(5)))
tmpf = 'tmp_' + ext
#client_ip_list = []
#nodeip_list = []
client_area_list = []
all_node_ip_list = []
node_area_list = []
node_isp_list = []
cover_isp_list = []
tmp_client_ip_area = ''
error_client_ip = []

ctl_client_area_list = []
cnc_client_area_list = []
cmb_client_area_list = []
crc_client_area_list = []
gwb_client_area_list = []
cer_client_area_list = []

ctl_node_area_list = []
cnc_node_area_list = []
cmb_node_area_list = []
crc_node_area_list = []
gwb_node_area_list = []
cer_node_area_list = []

ctl_node_isp_list = []
cnc_node_isp_list = []
cmb_node_isp_list = []
crc_node_isp_list = []
gwb_node_isp_list = []
cer_node_isp_list = []

ctl_cover_isp_list = []
cnc_cover_isp_list = []
cmb_cover_isp_list = []
crc_cover_isp_list = []
gwb_cover_isp_list = []
cer_cover_isp_list = []

xj_fullname = '新疆维吾尔自治区'.decode("utf8")
gx_fullname = '广西壮族自治区'.decode("utf8")
nx_fullname = '宁夏回族自治区'.decode("utf8")
xz_fullname = '西藏自治区'.decode("utf8")
nm_fullname = '内蒙古自治区'.decode("utf8")

def usage():
    help_info = colored('''
####################################################################################################################################

        此脚本用于在linux 终端快速查询 CDN 全国被调度哪些区域节点的工具,实际上是类似下面命令的封装：

        dig @119.29.29.29 www.baidu.com  +client=218.203.160.194

        维护：赵子发, avyou55@gmail.com

        url: https://github.com/avyou/CDN_dig

        用法: cdig -d <--domain> [-h <--help>] [-i,--ip>] [-a,--isp] [-n,--edns]

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

#####################################################################################################################################
    ''' %os.path.basename(ipdns_db),'yellow')
    print help_info
    sys.exit(2)

def area_Replace(func):
    def wrapper(*args,**kwargs):
        area = func(*args,**kwargs)
        if xj_fullname in area:
            area  = re.sub(xj_fullname,'新疆'.decode("utf8"),area)
        if xz_fullname in area:
            area = re.sub(xz_fullname,'西藏'.decode("utf8"),area)
        if nm_fullname in area:
            area = re.sub(nm_fullname,'内蒙古'.decode("utf8"),area)
        if gx_fullname in area:
            area = re.sub(gx_fullname,'广西'.decode("utf8"),area)
        if nx_fullname in area:
            area = re.sub(nx_fullname,'宁夏'.decode("utf8"),area)

        if len(area.split()) == 3:
            area = area.split()[0] + " " + area.split()[-1]

        return area
    return wrapper

##打开客户IP列表文件,读取放入列表
def dns_ip_list(filename):
    ip_list = []
    with open(filename,'r') as f:
        for i in f.readlines():
            if len(i) == 0:
                continue
            ##一个元组，分别是IP和ISP别名
            ip_list.append(i.strip().split())
    return ip_list

##输出的结果到临时文件
def writeLog(tmpf,info):
    with open(tmpf,'a') as f:
        try:
            f.write(info.get_string()+"\n")
        except:
            f.write(info+"\n")

def printinfo(domain,dns,show_on):
    if show_on == 1:
        info =  colored("\n################ 查询域名: %s,  使用DNS: %s 进行解析 ####################\n" %(domain,dns),'green')
        print info
        writeLog(tmpfile,info)

##使用 dig 解析出域名的信息，并过滤出IP
def dig_query(domain,edns,client_ip,show_on):
    ##取到的IP放到这里
    nodesip = []
    cname_list = []
    reobj_ip = re.compile(r'.*IN[\t| ]+?A[\t| ]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    reobj_cname = re.compile(r'.*IN[\t| ]+?CNAME[\t| ]+(.+)\.$')
    ###reobj_cname = re.compile(r'.*IN[\t| ]+?CNAME.*')
    ###dig @119.29.29.29  www.baidu.com +client=218.203.160.194
    if edns is None:
        edns = default_dns
        printinfo(domain,edns,show_on)

    else:
        edns = edns
        printinfo(domain,edns,show_on)
    try:
        #print '{0} +time=2 +tries=1  @{1} {2} +client={3}'.format(dig,edns,domain,client_ip)
        dig_cmd = os.popen('{0} +time=2 +tries=1  @{1} {2} +client={3}'.format(dig,edns,domain,client_ip)).readlines()
        for i in dig_cmd:
            if reobj_ip.match(i) is not None:
                #print reobj_ip.match(i).group(1)
                nodesip.append(reobj_ip.match(i).group(1))
            if reobj_cname.match(i) is not None:
                cname = reobj_cname.match(i).group(1)
                if cname not in cname_list:
                    cname_list.append(cname)
        if len(nodesip) == 0:
            #print colored("域名: %s, DNS: %s, IP %s, 域名解析失败! 请检查." %(domain,edns,client_ip),'red')
            nodesip.append("not ok")
            error_client_ip.append(client_ip)
    except Exception as e:
        print colored("域名: %s, DNS: %s, IP %s, 命令解析异常! 请检查:%s" %(domain,edns,client_ip,e),'red')

    return nodesip,cname_list


##请求API ，返回IP的区域地址

@area_Replace
def ip_api(ip,api):
    query_ip = QueryIP(api_dict,ip,api)
    area = query_ip.area
    if area == "unknown":
        for i in api_dict:
            if i != api:
                query_ip = QueryIP(api_dict,ip,i)
                area = query_ip.area
                if area != 'unknown':
                    break
    return area

def query_area(client_ip,nodeip,query_ip_show):
    ##临时IP的区域
    global tmp_client_ip_area
    ## 使用 query_ip_show 开关是为了减少同一个 client_ip 对公网 API的多次查询
    if query_ip_show == 1:
        client_ip_area = ip_api(client_ip,default_api)
        tmp_client_ip_area = client_ip_area
    else:
        client_ip_area = tmp_client_ip_area

    nodeip_area = ip_api(nodeip,default_api)
    ##截取区域地址前部分内容
    client_isp_str = ''.join(list(unicode(re.split(u' ',client_ip_area)[0]))[0:2]) + '|' + re.split(u' ',client_ip_area)[-1]
    node_isp_str = ''.join(list(unicode(re.split(u' ',nodeip_area)[0]))[0:2]) + '|' + re.split(u' ',nodeip_area)[-1]

    ##检查点数，客户端的区域地址放到一个列表
    if client_ip_area not in client_area_list:
        client_area_list.append(client_ip_area)

    ##所有CDN节点
    if (nodeip not in all_node_ip_list) and nodeip != "not ok":
        node_area_list.append(nodeip_area)
        all_node_ip_list.append(nodeip)

    #if nodeip_area not in node_area_list:
    #    node_area_list.append(nodeip_area)

    ##省节点数
    if (node_isp_str not in node_isp_list) and 'unknown' not in node_isp_str:
        #print node_isp_str
        node_isp_list.append(node_isp_str)

    ##本省覆盖
    if (client_isp_str == node_isp_str) and  (node_isp_str not in cover_isp_list):
        cover_isp_list.append(node_isp_str)

    return client_ip_area,nodeip_area

## 运营商区域数计算
def stat_isp():
    ##之所以用列表，而不用累加，是方便以后可能扩展要显示里面的内容
    ##print client_area_list

    ##检查点
    for i in client_area_list:
        isp = i.split()[-1]
        #print isp
        if isp == '电信':
            ctl_client_area_list.append(i)
        if isp == '联通':
            cnc_client_area_list.append(i)
        if isp == '移动':
            cmb_client_area_list.append(i)
        if isp == '铁通':
            crc_client_area_list.append(i)
        if isp == '长城宽带':
            gwb_client_area_list.append(i)
        if isp == '教育网':
            cer_client_area_list.append(i)

    ##全国节点
    for i in node_area_list:
        isp = i.split()[-1]
        if isp == '电信':
            ctl_node_area_list.append(i)
        if isp == '联通':
            cnc_node_area_list.append(i)
        if isp == '移动':
            #print i,isp
            cmb_node_area_list.append(i)
        if isp == '铁通':
            crc_node_area_list.append(i)
        if isp == '长城宽带' or isp == '鹏博士宽带':
            gwb_node_area_list.append(i)
        if isp == '教育网':
            cer_node_area_list.append(i)

    ##省节点数
    for i in node_isp_list:
        isp = i.split('|')[-1]
        if isp == '电信':
            ctl_node_isp_list.append(i)
        if isp == '联通':
            cnc_node_isp_list.append(i)
        if isp == '移动':
            cmb_node_isp_list.append(i)
        if isp == '铁通':
            crc_node_isp_list.append(i)
        if isp == '长城宽带':
            gwb_node_isp_list.append(i)
        if isp == '教育网':
            cer_node_isp_list.append(i)

    ##本省覆盖
    for i in cover_isp_list:
        isp = i.split('|')[-1]
        if isp == '电信':
            ctl_cover_isp_list.append(i)
        if isp == '联通':
            cnc_cover_isp_list.append(i)
        if isp == '移动':
            cmb_cover_isp_list.append(i)
        if isp == '铁通':
            crc_cover_isp_list.append(i)
        if isp == '长城宽带':
            gwb_cover_isp_list.append(i)
        if isp == '教育网':
            cer_cover_isp_list.append(i)


def getline(dns_p_list,ip_list,domain,edns,show_on,tqdm_on):
    if tqdm_on == 1:
        ip_list = tqdm(ip_list)
    for client_ip,client_isp_alias in ip_list:
        nodes_ip,cnames = dig_query(domain,edns,client_ip,show_on)
        show_on = 0
        query_ip_show = 1
        for node_ip in nodes_ip:
            client_ip_area,nodeip_area = query_area(client_ip,node_ip,query_ip_show)
            query_ip_show = 0
            ## 表格每一行要显示的内容
            if len(cnames) != 0:
                lineinfo = [client_ip,client_ip_area,client_isp_alias,cnames[0],cnames[-1],node_ip,nodeip_area]
            else:
                lineinfo = [client_ip,client_ip_area,client_isp_alias,'','',node_ip,nodeip_area]

            if node_ip == "not ok":
                error = colored("not ok",'red')
                lineinfo = [client_ip,client_ip_area,client_isp_alias,'','',error,error]
            dns_p_list.append(lineinfo)

def check_dig_soft(dig_bin):
    if not os.path.exists(dig_bin):
        print "未安装支持 edns的dig软件"
        sys.exit(65)
    edns_support = os.popen("%s -h|grep client|grep -v grep" % dig_bin).read()
    if len(edns_support) == 0:
        print colored("\nSorry,您安装的dig软件不支持EDNS功能!\n",'red')
        sys.exit(65)
        


##表格处理显示
def output_tables(domain,edns,client_ip=None,area=None):
    ## 全国节点解析表格
    dns_parse_t = PrettyTable(["Client IP", "Client ISP","Alias","First CNAME","Last CNAME","Node IP", "Node IP ISP"])
    ## 统计表格
    isp_stat_t = PrettyTable(['运营商',"检查点数", "全国节点数","省节点数(同省算1)","本省覆盖数"])
    ## 记录信息
    record_t = PrettyTable(['Description',"Logfile"])
    ##对齐方式
    dns_parse_t.padding_width = 1
    dns_parse_t.align["Client IP"] = "l"
    dns_parse_t.align["Client ISP"] = "l"
    dns_parse_t.align["Alias"] = "l"
    dns_parse_t.align["First CNAME"] = "l"
    dns_parse_t.align["Last CNAME"] = "l"
    dns_parse_t.align["Node IP"] = "l"
    dns_parse_t.align["Node IP ISP"] = "l"
    dns_parse_data_list = []
    ##返回一个元组列表，全国需要调用的 client IP 列表，包含ISP别名
    ip_list = dns_ip_list(ipdns_db)
    #print ip_list

    ##ISP覆盖统计显示默认为0，不显示
    stat_show = 0
    global show_on
    ##如果只查询域名，不指定IP或区域,显示全部
    ##如果输入参数中没有指定client IP, 且 ISP 也没有指定，则默认全部解析，并显示全部
    if client_ip is None and area is None:
        ##显示ISP统计
        stat_show = 1
        info =  "\n=============== 正在调用全国IP解析,请稍候... ==============="
        print info
        writeLog(tmpfile,info)
        ##读取
        show_on = 1
        getline(dns_parse_data_list,ip_list,domain,edns,show_on,1)

    elif set(area.split(',')).issubset(all_isp) and client_ip is None:
        stat_show = 1
        show_on = 1
        info =  "\n=============== 正在调用全国IP解析,请稍候... ==============="
        print info
        writeLog(tmpfile,info)
        isp_ip_list = []
        ##0或多个ISP的情况
        for area_i in area.split(','):
            #print area_i
            t_list = [ i for i in ip_list if i[1].split('-')[0] == area_i ]
            isp_ip_list.extend(t_list)

        getline(dns_parse_data_list,isp_ip_list,domain,edns,show_on,1)
    else:
        if area is not None and area not in all_isp and client_ip is None:
            isp_ip_list = []
            for area_i in area.split(',') :
                try:
                    t_list = [ip for ip in ip_list if ip[1] == area_i ]
                    isp_ip_list.extend(t_list)
                except:
                    ##如果没有对应的 ISP在文件，显示错误
                    print colored('错误： %s 文件中不包含 "%s" 此区域的IP\n' %(ipdns_db,area),'red')
                    sys.exit(2)
        else:
            isp_ip_list = [client_ip,'']

        getline(dns_parse_data_list,isp_ip_list,domain,edns,1,0)

    for line in dns_parse_data_list:
        dns_parse_t.add_row(line)
    print dns_parse_t
    writeLog(tmpfile,dns_parse_t)

    if stat_show == 1:
        stat_isp()
        isp_stat_t.add_row(['电信',len(ctl_client_area_list),len(ctl_node_area_list),len(ctl_node_isp_list),len(ctl_cover_isp_list)])
        isp_stat_t.add_row(['联通',len(cnc_client_area_list),len(cnc_node_area_list),len(cnc_node_isp_list),len(cnc_cover_isp_list)])
        isp_stat_t.add_row(['移动',len(cmb_client_area_list),len(cmb_node_area_list),len(cmb_node_isp_list),len(cmb_cover_isp_list)])
        isp_stat_t.add_row(['铁通',len(crc_client_area_list),len(crc_node_area_list),len(crc_node_isp_list),len(crc_cover_isp_list)])
        isp_stat_t.add_row(['长宽',len(gwb_client_area_list),len(gwb_node_area_list),len(gwb_node_isp_list),len(gwb_cover_isp_list)])
        isp_stat_t.add_row(['教育网',len(cer_client_area_list),len(cer_node_area_list),len(cer_node_isp_list),len(cer_cover_isp_list)])
        isp_stat_t.add_row(['总合',len(client_area_list),len(node_area_list),len(node_isp_list),len(cover_isp_list)])
        print colored(isp_stat_t,'green')
        writeLog(tmpfile,isp_stat_t)

    # result_log=colored('\n########################  内容同时输出到文件: %s ######################\n' %tmpfile,'yellow')
    # print colored('\n########################  节点唯一IP输出到文件: %s ######################\n' %node_tmpfile,'green')

    record_t.padding_width = 1
    record_t.align["Description"] = "l"
    record_t.align["Logfile"] = "l"
    record_t.add_row([colored('内容同时输出到:','yellow'),colored(tmpfile,'yellow')])
    record_t.add_row([colored('节点唯一IP输出:','green'),colored(node_tmpfile,'green')])
    print record_t

    all_node = ''
    for node in all_node_ip_list:
        all_node = all_node + node + "\n"
    writeLog(node_tmpfile,all_node)

def main():
    import ConfigParser

    global default_api
    global ipdns_db
    global dig
    global default_dns
    global all_isp
    global tmp_dir
    global api_dict
    global tmp_dir
    global tmpfile,node_tmpfile
    global config_file

    package_path = os.path.dirname(os.path.realpath(__file__))

    cf = ConfigParser.ConfigParser()
    config_file = '/usr/local/CDN_dig/etc/config.ini'
    try:
        cf.read(config_file)
    except:
        try:
            cf.read('.data/config.ini')
        except Exception as e:
            print "读取配置文件出错:%s" %e 
            sys.exit(65)
    else:
        try:
            default_api = cf.get('BASE','default_api')
        except:
            default_api = 'ip138'
        ##全国DNS列表库
        try:
            ipdns_db = cf.get('BASE','ipdns_db')
            if not os.path.exists(ipdns_db):
                ipdns_db = os.path.join(package_path,ipdns_db)
        except:
            ipdns_db = os.path.join(package_path,ipdns_db)

        ##默认使用的EDNS
        try:
            default_dns = cf.get('BASE','default_dns')
        except:
            default_dns = '119.29.29.29'
        ## dig 二进制程序路径
        dig = cf.get('BASE','dig')
        check_dig_soft(dig)
        ##输出的日志路径
        tmp_dir = cf.get('BASE','tmp_dir')
        ##查询IP接口
        api_dict = {}
        for opt,val in cf.items("API"):
            api_dict[opt] = val

    all_isp = ['cmb','ctl','cnc','gwb','crc','cer']
    node_tmpfile = os.sep.join([tmp_dir,'node_' + tmpf])
    ##输出的临时文件
    tmpfile = os.sep.join([tmp_dir,tmpf])
    ##创建临时目录
    if not  os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    try:
        ##传参数选项
        opts,args = getopt.getopt(sys.argv[1:],"hi:a:n:d:",["help","domain=","ip=","edns=","isp="])
    except getopt.GetoptError:
        usage()

    domain = None
    client_ip = None
    area = None
    edns = None

    for opt,arg in opts:
        if opt == ('-h','--help'):
            usage()
        elif opt in ("-d","--domain"):
            domain = arg
        elif opt in ("-i","--ip"):
            client_ip = arg
        elif opt in ("-a","--isp"):
            area = arg
        elif opt in ("-n","--edns"):
            edns = arg
        else:
            usage()
    if domain is None:
        usage()
    output_tables(domain,edns,client_ip,area)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
    main()
