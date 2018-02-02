#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Query the area where the IP is located
# by avyou
# 20171226

#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from lxml import etree
import requests, re
import simplejson as json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os

class QueryIP(object):
    def __init__(self,api_dict,ip,api="nali3"):
        self.api_dict = api_dict
        self.ip = ip
        self.api = api
        self.api_dict_area = {}
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
        self.selectAPI()

    def query_taobao(self,url):
        url = url  + self.ip
        r = requests.get(url,headers=self.headers)
        data = r.content
        if r.status_code == 200 and len(data) !=0 :
            api_data = json.loads(data)
            self.area = '%s%s-%s %s' %(api_data["data"]["country"],api_data["data"]["city"],api_data["data"]["area"],api_data["data"]["isp"])
        else:
            self.area = 'unknown'

    def query_ip138(self,url):
        url = url  + self.ip
        try:
            r = requests.get(url,headers=self.headers)
            data = r.content
            if r.status_code == 200 and len(data) != 0:
                html = unicode(data, 'gb2312')
                pattern = re.compile(ur'<li>本站数据：(.*?)</li>')
                m = pattern.search(html)
                if m:
                    self.area = m.group(1).strip()
                else:
                    self.area = 'unknown'
        except:
            self.area = 'unknown'

    def query_ipcn(self,url):
        url = url + self.ip
        r = requests.get(url,headers=self.headers)
        data = r.text
        if r.status_code == 200 and len(data) !=0:
            html = etree.HTML(data)
            try:
                str_data = html.xpath("//*[@class='well']/p[2]/code/text()")
                print str_data
                self.area = str_data[0]
            except:
                self.area = 'unknown'
        else:
            self.area = 'unknown'

    ##使用浏览器内核模拟，比较慢
    def query_ipip_webdriver(self,url):
        #driver = webdriver.Chrome()
        driver = webdriver.Firefox()
        driver.get(url)
        elem = driver.find_element_by_name("ip")
        elem.send_keys(self.ip)
        elem.send_keys(Keys.RETURN)
        assert  "not results found." not in driver.page_source
        html = driver.page_source
        driver.close()
        html = etree.HTML(html)
        src_area = html.xpath("//*[@id='myself']/text()")
        self.area = src_area[0].strip()

    def query_ipip_free(self,url):
        url = url + self.ip
        r = requests.get(url,headers=self.headers)
        data = r.text
        if r.status_code == 200 and len(data) != 0:
            data_dict  = json.loads(data)
            if data_dict[1] == data_dict[2]:
                self.area = "{0}{1} {2}".format(data_dict[1],data_dict[3],data_dict[-1])
            else:
                self.area = "{0}{1}{2} {3}".format(data_dict[1],data_dict[2],data_dict[3],data_dict[-1])
        else:
            self.area = 'unknown'

    def query_ipip_db(self,db):
        try:
            from ipip import IP
            IP.load(os.path.abspath(db))
            data = IP.find(self.ip)
            self.area = data.split()[1] + data.split()[2] + " " + data.split()[-1]
        except:
            self.area = "unknown"

    def query_chinaz(self,url):
        url = url + self.ip
        r = requests.post(url)
        data = r.text
        if r.status_code == 200 and len(data) != 0:
            html = etree.HTML(data)
            data = html.xpath("//*[@class='Whwtdhalf w50-0']/text()")
            str_area1 = data[1].split()[0]
            try:
                str_area2 = data[1].split()[1]
                if re.match("电信".decode("utf8"),str_area2.decode("utf8")):
                    str_area2 = "电信"

                if re.match("联通".decode("utf8"),str_area2.decode("utf8")):
                    str_area2 = "联通"

                if re.match("移动".decode("utf8"),str_area2.decode("utf8")):
                    str_area2 = "移动"
                self.area = str_area1 + " " +  str_area2
            except:
                self.area = str_area1
        else:
            self.area = 'unknown'

    def query_nali3(self,cmd):
       try:
           data = os.popen('%s  %s' %(cmd,self.ip)).read().strip().split()[1]
           t1 = data.lstrip("[").rstrip("]").split("-")[1:]
           #if len(t1) >3:
           #    t1.insert(1,'省')
           #    t1.insert(3,'市')
           t2 = list(set(t1))
           t2.sort(key=t1.index)
           if len(t2) >= 2:
               t2.insert(-1," ")
           self.area = "".join(t2)
           
       except:
           self.area = "unknown"

    def query_qqwry(self,db):
        try:
            from qqwry import QQwry
            q = QQWry()
            q.load_file('db')
            self.area = q.lookup(self.ip)
        except:
            self.area = 'unknown'

    def selectAPI(self):
        if self.api == "ip138":
            self.query_ip138(self.api_dict[self.api])
        elif self.api  == "taobao":
            self.query_taobao(self.api_dict[self.api])
        elif self.api  == "ipip_free":
            self.query_ipip_free(self.api_dict[self.api])
        elif self.api  == "ipcn":
            self.query_ipcn(self.api_dict[self.api])
        elif self.api == "chinaz":
            self.query_chinaz(self.api_dict[self.api])
        elif self.api == 'ipdb':
            self.query_ipip_db(self.api_dict[self.api])
        elif self.api == 'nali3':
            self.query_nali3(self.api_dict[self.api])
        elif self.api == 'qqwry':
            self.query_qqwry(self.api_dict[self.api])
        else:
            print "接口名称错误"
            self.area = "unknown"

        self.api_dict_area[self.api] = self.area

    def allAPI(self):
        for api in self.api_dict:
            self.api = api
            self.selectAPI()
        return self.api_dict_area

if  __name__ == "__main__":
    api_dict = {
        "ip138":"http://www.ip138.com/ips138.asp?ip=",
        "taobao":"http://ip.taobao.com//service/getIpInfo.php?ip=",
        "ipip":"http://www.ipip.net/ip.html",
        "ipip_free":"http://freeapi.ipip.net/",
        "ipcn":"http://ip.cn/index.php?ip=",
        "chinaz":"http://ip.chinaz.com/",
        "ipdb":"/usr/local/cdn_dig/data/ipipdb.dat",
        "nali3":"/usr/local/bin/nali3",
        "qqwry":"/usr/local/cdn_dig/data/qqwry.dat"
    }
    ip = sys.argv[1]
    query_ip = QueryIP(api_dict,ip)
    ip_area_dict  = query_ip.allAPI()
    for name,area in ip_area_dict.items():
        print "%s :%s" %(name,area)
