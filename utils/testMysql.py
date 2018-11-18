# # import pymysql
# # import time
# #
# # # 开启数据库
# # db = pymysql.connect("47.95.219.28", "yxc", "123456", "PyScrapy", charset="utf8")
# #
# # # 定义游标
# # cursor = db.cursor()
# # sql = "select ip from t_ip_20181118113414;"
# # cursor.execute(sql)
# # ips = cursor.fetchall()
# # # print(ips)
# # ipArrays = []
# # for ip in ips:
# #     ip = str(ip)
# #     ip = ip.replace("('","")
# #     ip = ip.replace("',)","")
# #     ip = ip.replace(" ","")
# #     ipArray = ip.split(":")
# #     ipArrays.append(ipArray)
# #     # print(ipArray)
# # print(ipArrays)
# #
# #
# #
# # # 删除数据
# # sql = "delete from t_ip"
# # cursor.execute(sql)
# # db.commit()
# #
# # # 更新掉数据
# # now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# # for ip,port in ipArrays:
# #     # print(ip+"   "+port)
# #     sql = "insert into t_ip(ip,port,create_date) values ('{0}','{1}','{2}')".format(ip, port, now_time)
# #     cursor.execute(sql)
# #     db.commit()
# # db.close()
# # # db.commit()
# # # sql = "insert into t_ip(ip,create_time) values ('{0}',{1})".format()
#
#
# 导入requests的包 用来网络请求
import requests
# 导入lxml的包  使用xPath
from lxml import html
# 随机数  从ipPools中随机取ip
import random
# 导入自定义的获取远程ip的类
from utils import getIpsFromRemotes
# 导入数据库连接包
import pymysql
# 导入线程的包
import threading
# 导入时间包
import time
#
# # 浏览器的请求头
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
# }
# url = "http://www.17jita.com/tab/whole_6945.html"
# text = requests.get(url=url,headers = HEADERS).text
# selector = html.fromstring(text)
# hrefs = selector.xpath("//td[@id='article_contents']/a/@href")
# print(hrefs)
#
#
#
#
#
#
#
#
#
#

MYSQL_URL = "47.95.219.28"
MYSQL_NAME = "yxc"
MYSQL_PASSWORD = "123456"
MYSQL_DATABASE = "PySongs"


def connect2Mysql():
    """
    获取数据库链接
    :return:
    """
    return pymysql.connect(MYSQL_URL, MYSQL_NAME, MYSQL_PASSWORD, MYSQL_DATABASE, charset="utf8")

db = connect2Mysql()
cursor = db.cursor()
cursor.execute("select song_name,href from t_song_list where href like 'tab/img/%'")
result = cursor.fetchall()
for name, href in result:
    print(href)
# print(result)