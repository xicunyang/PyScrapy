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

# _*_coding:utf-8_*_

# 浏览器的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}
MYSQL_URL = "47.95.219.28"
MYSQL_NAME = "yxc"
MYSQL_PASSWORD = "123456"
MYSQL_DATABASE = "PySongs"


def connect2Mysql():
    """
    获取数据库链接
    :return: 数据库连接信息
    """
    return pymysql.connect(MYSQL_URL, MYSQL_NAME, MYSQL_PASSWORD, MYSQL_DATABASE, charset="utf8")


def backupTable(tableName):
    """
    备份表
    :param tableName: 表名
    :return: Null
    """
    db = connect2Mysql()
    cursor = db.cursor()
    now_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    sql = "create table t_{0}_{1}(id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY) AS ( SELECT * FROM {0})".format(
        tableName, now_time)
    cursor.execute(sql)
    db.commit()

    # 再清空表
    sql = "delete from {0};".format(tableName)
    cursor.execute(sql)
    db.commit()
    db.close()


def getIpsFromDatabase():
    """
    从数据库内获取ip列表
    :return: ip列表
    """
    db = getIpsFromRemotes.connect2Mysql()
    cursor = db.cursor()
    sql = "select ip,port from t_ip;"
    cursor.execute(sql)
    return cursor.fetchall()


def getRandomIp():
    """
    获取随机ip
    :return: {ip: port}
    """
    global ipPools_g
    myRamdom = random.randint(0, len(ipPools_g) - 1)
    ip, port = ipPools_g[myRamdom]
    return {ip: port}


def getSingerListFromRemote():
    """
    从远程获取到歌手列表的相应信息
    :return: Null
    """
    print("获取歌手列表页信息开始......")
    global singerInfos_g
    singerInfos_local = []
    singerInfos_local2 = []
    for i in range(1, 7):
        url = "http://www.17jita.com/tab/singer/index.php?page=" + str(i)
        resultInfo = requests.get(url, headers=HEADERS, proxies=getRandomIp()).text
        selector = html.fromstring(resultInfo)
        # 链接后缀
        hrefs = selector.xpath("//div[@class='bm_c xld']/ul/li/a[1]/@href")
        # 图片
        images = selector.xpath("//div[@class='bm_c xld']/ul/li/a/img/@src")
        # 歌手姓名
        singerNames = selector.xpath("//div[@class='bm_c xld']/ul/li/a[2]/strong/text()")
        singerInfos_local.append(zip(singerNames, images, hrefs))
    print("获取歌手列表页信息结束......")
    # 处理数据
    for singerInfo in singerInfos_local:
        for singerName, image, href in singerInfo:
            # 注意  这里不能用{}字典，因为字典是无序的
            info = [singerName, image, href]
            singerInfos_local2.append(info)

    singerInfos_g = singerInfos_local2
    # 将获取到的歌手信息存入数据库
    choose = input("是否存入将歌手信息数据库? y/n")
    if choose == "y":
        saveSingerInfo2Database(singerInfos_g)
    else:
        getSongsList()


def saveSingerInfo2Database(singerInfos):
    """
    将歌手列表信息存到数据库
    :param singerInfos: 歌手信息列表集合
    :return: Null
    """
    print("存入歌手列表页信息开始......")
    db = connect2Mysql()
    cursor = db.cursor()
    # 先清空表
    sql = "delete from t_singer_info;"
    cursor.execute(sql)
    db.commit()

    # 存入数据
    for singerName, image, href in singerInfos:
        sql = "insert into t_singer_info(singer_name,singer_image,singer_href)" \
              " values('{0}','{1}','{2}');".format(singerName, image, href)
        cursor.execute(sql)
        db.commit()
    db.close()

    # 开始获取歌手详细页面
    print("存入歌手列表页信息结束......")
    getSongsList()


def saveSongList2Database(songLists):
    """
    将信息存入数据库
    :param songLists:
    :return: Null
    """
    mutex.acquire()
    db = connect2Mysql()
    cursor = db.cursor()

    # 添加操作
    for songName, href in songLists:
        songName = str(songName).replace("(", "<")
        songName = songName.replace(")", ">")
        songName = songName.replace("'", "")
        sql = "insert into t_song_list(song_name,href) values('{0}','{1}')".format(songName, href)
        print(sql)
        cursor.execute(sql)
        db.commit()
    # 关闭数据库连接
    db.close()
    mutex.release()


def getSongsListThread(start, end):
    """
    获取歌曲列表的子线程实现函数
    :param start: 歌手列表的起始位置
    :param end: 歌手列表的结束位置
    :return: Null
    """
    print("线程" + threading.current_thread().getName() + "启动......")
    global singerInfos_g
    global songListInfos_g
    # 得到切片后的歌手列表
    localsingerInfos = singerInfos_g[start:end]
    songLists = []
    songLists2 = []
    for i in range(0, len(localsingerInfos)):
        name, image, href = localsingerInfos[i]
        href = "http://www.17jita.com/" + href
        # 根据href去请求
        r = requests.get(url=href, headers=HEADERS, proxies=getRandomIp())
        # 由于页面使用的是GBK编码  所以用utf-8获取的时候会是乱码  故此处是使用GBK
        r.encoding = "GBK"
        selector = html.fromstring(r.text)
        songNames = selector.xpath("//td[@id='article_content']/ul/li/a[2]/text()")
        hrefs = selector.xpath("//td[@id='article_content']/ul/li/a[2]/@href")
        songLists.append(zip(songNames, hrefs))

    for singerSongList in songLists:
        for songName, href in singerSongList:
            list = [songName, href]
            songLists2.append(list)

    songListInfos_g = songLists2
    saveSongList2Database(songLists2)


def getSongsList():
    """
    根据歌手信息获取该歌手下的所有歌曲
    :return: Null
    """
    # 备份表
    backupTable("t_song_list")
    # 分配线程池
    songListThreads = []
    global singerInfos_g
    step = 10
    for i in range(1, 17):
        start = step * i - 10
        end = step * i - 1
        songListThreads.append(threading.Thread(target=getSongsListThread, args=(start, end)))
    for t in songListThreads:
        t.start()
    for t in songListThreads:
        t.join()

    # 等线程都执行完就去获取所有歌曲内的详细图片
    getPicInfo()


def getPicInfo():
    """
    根据歌手的下的歌曲信息  爬取该歌曲的相应的吉他谱
    :return: Null
    """
    # 从数据库获取数据
    db = connect2Mysql()
    cursor = db.cursor()
    cursor.execute("select song_name,href from t_song_list where href like 'tab/img/%'")
    result = cursor.fetchall()
    # 根据返回值进行获取数据即可...


if __name__ == '__main__':
    mutex = threading.Lock()
    # ip代理池
    ipPools_g = []
    # 歌手页的信息
    singerInfos_g = []
    # 歌手内的歌曲信息
    songListInfos_g = []
    choose = input("是否从远程获取到最新的ip代理池? y/n")
    if choose == "y":
        # 更新代理池
        getIpsFromRemotes.start()
    # 不更新代理池  正常操作
    # 先从mysql中获取的ip代理池
    ipPools_g = getIpsFromDatabase()
    # 共6页热门歌手  就单线程获取
    getSingerListFromRemote()
