#!/usr/bin/env python
#-*- coding:utf-8 -*-
# by avyou
# at 20180201

import os
import sys
import re
import urllib2
import simplejson as json
import requests, re
import ConfigParser
from  models.queryIP import QueryIP
reload(sys)
sys.setdefaultencoding("utf-8")


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

def match_rr_file(matched):
   ip = matched.group('ip')
   area = ip_api(ip,api)
   output = "{0:15} [{1}]".format(ip,area)
   return output

def match_rr(matched):
   ip = matched.group('ip')
   area = ip_api(ip,api)
   output = "{0} [{1}]".format(ip,area)
   return output

def replace_show(src,isfile):
    re_obj = re.compile('(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    try:
        if isfile == 0:
            print re_obj.sub(match_rr,src)
        else:
            print re_obj.sub(match_rr_file,src)
    except Exception as e:
        print "Error read: %s" % e
        sys.exit(65)
    

def read_input():
    isfile = 0 
    input_arg =  sys.argv[1:]
    input_info = ""
    if len(input_arg) == 1:
        if os.path.isfile(input_arg[0]):
            try:
                f = file(input_arg[0],'r')
                input_info = f.read().strip()
                isfile = 1
            except:
                input_info = input_arg[0]
            finally:
                f.close()            
        else:
            input_info = input_arg[0]
    else:
        input_info = " ".join(input_arg)
    if not sys.stdin.isatty():
        input_info = sys.stdin.read().strip()
        isfile = 1

    replace_show(input_info,isfile)

def main():
    global api
    global config_file
    global api_dict

    package_path = os.path.dirname(os.path.realpath(__file__))
    cf = ConfigParser.ConfigParser()
    config_file = '/usr/local/CDN_dig/etc/config.ini'
    try:
        cf.read(config_file)
    except:
        try:
            cf.read('.data/config.ini')
        except Exception as e:
            api = 'ip138'
            api_dict = {
                "ip138":"http://www.ip138.com/ips138.asp?ip=",
                "chinaz":"http://ip.chinaz.com/",
                "qqwry":"/usr/local/CDN_dig/data/qqwry.dat",
            }
    else:
        try:
            api = cf.get('BASE','default_api')
        except:
            api = 'ip138'
        api_dict = {}
        for opt,val in cf.items("API"):
            api_dict[opt] = val

    read_input()

if __name__ == '__main__':
    main()
