# 导入线程的包
import threading
# 导入requests的包 用来网络请求
import requests
# 导入lxml的包  使用xPath
from lxml import html
# 导入mysql
import pymysql
# 导入时间
import time

# 浏览器的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}

# URL = "https://www.kuaidaili.com/free/inha/1/"
# 根据末尾的数字进行获取不同页数
URL = "http://www.xicidaili.com/nn/"

requests.get(url=URL, headers=HEADERS)


def getRemotePageInfo(pageNum):
    url = URL + str(pageNum);
    # print(url)
    # 根据url去请求页面信息
    resultText = requests.get(url, headers=HEADERS).text
    # print(resultText)
    selector = html.fromstring(resultText)
    ips = selector.xpath("//table[@id='ip_list']/tr[@class='odd']/td[2]/text()")
    ports = selector.xpath("//table[@id='ip_list']/tr[@class='odd']/td[3]/text()")
    IPS = zip(ips, ports)
    testRemoteIps(IPS)


def testRemoteIps(IPS):
    # 定义成功的ip
    successIps = []
    for ip, port in IPS:
        # 远程连接百度  测试ip的可用性
        testIp = {ip: port}
        url = "https://www.baidu.com"
        try:
            requests.get(url=url, headers=HEADERS, proxies=testIp)
            # ip测试成功
            successIps.append(testIp)
        except:
            print("ip error")

    # print(successIps)
    # 测试成功  成功得到能用的ip
    # 将能用的ip存入数据库  下次可以调用
    saveIpsToDatebases(successIps)


def saveIpsToDatebases(successIps):
    mutex.acquire()
    db = pymysql.connect("47.95.219.28", "root", "123456", "library", charset="utf8")
    cursor = db.cursor()
    nowDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # print(nowDate)
    for ip in successIps:
        sql = "insert into t_ip(ip,create_time) values ('{0}','{1}')".format(ip, nowDate)
        print(sql)
        cursor.execute(sql)
        db.commit()
    db.close()
    mutex.release()


if __name__ == '__main__':
    # 这是main函数
    # 这个是线程的锁
    mutex = threading.Lock()
    # 定义5个子线程个数
    threads = []
    threadCount = 5
    # 分配线程
    for t in range(1, threadCount + 1):
        # args是可以穿一个元组  当时一个参数的时候  加一个 逗号
        threads.append(threading.Thread(target=getRemotePageInfo, args=(t,)))
    # 开启线程
    for t in threads:
        t.start()
    # join线程
    # 作用  让主线程执行完进入阻塞状态 等子线程执行完  再结束
    for t in threads:
        t.join()

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
#
#
#
# #
