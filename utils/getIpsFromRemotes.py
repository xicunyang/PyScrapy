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

# 根据末尾的数字进行获取不同页数
URL = "http://www.xicidaili.com/nn/"
# 数据库的相关参数
MYSQL_URL = "47.95.219.28"
MYSQL_NAME = "yxc"
MYSQL_PASSWORD = "123456"
MYSQL_DATABASE = "PyScrapy"


def connect2Mysql():
    """
    连接数据库 封装
    :return:
    """
    return pymysql.connect(MYSQL_URL, MYSQL_NAME, MYSQL_PASSWORD, MYSQL_DATABASE, charset="utf8")


def getRemotePageInfo(pageNum):
    """
    从远程获取到西祠代理的ip页面
    :param pageNum: 页面数
    :return: Null
    """
    print("线程" + threading.current_thread().getName() + "启动......")
    # 拼接URL
    url = URL + str(pageNum);
    # 根据url去请求页面信息
    ip = {'101.64.32.100':'808'}
    resultText = requests.get(url, headers=HEADERS, proxies=ip).text
    # 将页面信息转化为lxml对象
    selector = html.fromstring(resultText)
    # 进行xpath解析
    ips = selector.xpath("//table[@id='ip_list']/tr[@class='odd']/td[2]/text()")
    ports = selector.xpath("//table[@id='ip_list']/tr[@class='odd']/td[3]/text()")
    # 将ip port进行对应  打包成zip
    IPS = zip(ips, ports)
    # 调用测试方法  使用百度测试
    testRemoteIps(IPS)


def testRemoteIps(IPS):
    """
    测试从页面获取的ip列表是否可用
    :param IPS: 从页面获取的ip的打包
    :return: Null
    """
    print("线程" + threading.current_thread().getName() + "测试IP的可用性开始......")
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
    print("线程" + threading.current_thread().getName() + "测试IP的可用性结束......")
    saveIpsToDatebases(successIps)


def saveIpsToDatebases(successIps):
    """
    将测试可用的ip存入数据库 便于后期使用
    :param successIps:
    :return: Null
    """
    """
    使用线程的锁
    """
    mutex.acquire()
    print("线程" + threading.current_thread().getName() + "向数据库存入ip开始......")
    db = pymysql.connect("47.95.219.28", "root", "123456", "PyScrapy", charset="utf8")
    cursor = db.cursor()
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for ip, port in successIps:
        sql = "insert into t_ip(ip,port,create_date) values ('{0}','{1}','{2}')".format(ip, port, now_time)
        cursor.execute(sql)
        db.commit()
    db.close()
    mutex.release()
    print("线程" + threading.current_thread().getName() + "向数据库存入ip结束......")


def clearDatebase():
    """
    在执行往数据库存的时候  调用删除
    :return: Null
    """
    db = connect2Mysql()
    cursor = db.cursor()
    # 备份数据库
    # 获取当前时间
    print("备份表......")
    now_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    back_sql = "CREATE TABLE t_ip_{0}(id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY) AS ( SELECT * FROM t_ip);".format(
        now_time)
    cursor.execute(back_sql)
    db.commit()
    # 清空表内数据
    print("清除数据......")
    sql = "delete from t_ip"
    cursor.execute(sql)
    db.commit()
    db.close()


# if __name__ == '__main__':
def start():
    """
    main函数
    """
    # 执行前先将表内的数据清掉
    clearDatebase()
    # 这个是线程的锁
    global mutex
    mutex = threading.Lock()
    # 定义5个子线程个数
    threads = []
    # 获取5页足够了
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


# #
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
