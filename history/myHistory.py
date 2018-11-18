import requests
from lxml import html
import random
import pymysql
import threading
import time
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

testIp = {'183.159.84.41': '18118', '61.135.217.7': '80', '122.114.31.177': '808', '60.174.74.40': '8118',
          '183.159.95.67': '18118', '183.159.93.166': '18118', '223.241.116.229': '8010', '183.159.81.199': '18118',
          '183.159.95.90': '18118', '183.159.86.174': '18118', '112.115.57.20': '3128', '114.215.47.93': '3128',
          '119.28.112.130': '3128', '14.153.52.204': '3128', '122.72.18.34': '80', '211.159.177.212': '3128',
          '139.224.80.139': '3128', '120.78.182.79': '3128', '222.188.191.247': '6666', '202.120.37.202': '1080',
          '60.168.207.46': '18118', '119.28.138.104': '3128', '124.193.37.5': '8888', '118.212.137.135': '31288',
          '114.215.95.188': '3128', '223.241.116.23': '18118', '117.68.194.81': '18118', '183.159.82.176': '18118',
          '117.68.194.7': '18118', '49.81.10.55': '39600', '123.53.118.46': '29520', '183.159.84.173': '18118',
          '222.185.23.184': '6666', '110.73.30.246': '6666', '121.31.103.33': '6666', '112.114.76.176': '6668',
          '113.121.245.32': '6667', '116.28.106.165': '6666', '110.73.32.7': '6666', '111.124.231.101': '6668',
          '113.122.42.161': '6675', '110.72.20.245': '6673', '122.89.138.20': '6675'}
songCount = 0
songCountDB = 0
my_re = re.compile(r'[A-Za-z]')


def getIp():
    url = "http://www.xicidaili.com/"
    response = requests.get(url, headers=headers).content
    selector = html.fromstring(response)
    ip = selector.xpath("//tr[@class='odd']/td[2]/text()")
    duankou = selector.xpath("//tr[@class='odd']/td[3]/text()")
    return zip(ip, duankou)


# http://data.17jita.com/attachment/forum/201705/14/123505lsfwnbke3whzksse.png**
# http://data.17jita.com/attachment/forum/201705/14/123505r2k1dfnagnnxfibi.png**
# http://data.17jita.com/attachment/forum/201705/14/123506xui8wj1u3pq1qifz.png

def getSuccessdeIp():
    SuccssIp = {}
    step = 0
    for ip, dk in getIp():
        proxy = {ip: dk}
        url = "http://www.baidu.com/"
        try:
            requests.get(url, headers=headers, proxies=proxy).content
            SuccssIp[ip] = dk
            step += 1
            print("获取ip地址---" + str(step) + "个")
        except:
            pass
    print(SuccssIp)
    return SuccssIp


def getRandomIp():
    global ipslist
    MyRandom = random.randint(0, len(ipslist) - 1)
    ip, dk = ipslist[MyRandom]
    proxy = {ip: dk}
    return proxy


# 先获取歌手页--count
def getSingerPageCount():
    url = "https://www.17jita.com/tab/singer/index.php?page=1"
    response = requests.get(url, headers=headers, proxies=getRandomIp()).content
    selector = html.fromstring(response)
    pageCount = selector.xpath("//div[@class='pg']/a[last()-1]/text()")[0]
    # print(pageCount)
    return int(pageCount)


# getSingerPageCount()
# 获取每一页的歌手list，存入数据库
# list包括  歌手姓名+页面标示
def getSingerlist(num):
    url = "https://www.17jita.com/tab/singer/index.php?page=" + str(num)
    response = requests.get(url, headers=headers, proxies=getRandomIp()).content
    selector = html.fromstring(response)
    hrefList = selector.xpath("//div[@class='bm_c xld']/ul/li/a[last()]/@href")
    singerList = selector.xpath("//div[@class='bm_c xld']/ul/li/a[last()]/strong/text()")
    picList = selector.xpath("//div[@class='bm_c xld']/ul/li/a/img/@src")
    saveSingerList(zip(singerList, hrefList, picList))


def saveSingerList(singerInfos):
    global mutex
    mutex.acquire()
    global singerCount
    db = pymysql.connect("localhost", "root", "123456", "mypc", charset="utf8")
    cursor = db.cursor()
    for singer, href, pic in singerInfos:
        sql = "insert into guitar_singer(singer,pic,href) values('{0}','{1}','{2}')".format(singer, pic, href)
        cursor.execute(sql)
        db.commit()
        singerCount += 1
        print(singerCount)
    db.close()
    mutex.release()


def getSingerInfoFromDB():
    db = pymysql.connect("localhost", "root", "123456", "mypc", charset="utf8")
    cursor = db.cursor()
    sql = "select singer,href from guitar_singer"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        singerInfos = cursor.fetchall()
    except:
        print("Error: unable to fetch data")

    # print(singerInfos)
    db.close()
    return singerInfos


def getSongList(n, step, singerInfos):
    start = (n - 1) * step
    stop = (n * step)
    if stop > len(singerInfos):
        stop = len(singerInfos)

    for num in range(start, stop):
        flag = singerInfos[num - 1]

        url = "https://www.17jita.com/" + flag[1]
        print(url, "   -" + str(num) + "-")
        response = requests.get(url, headers=headers, proxies=getRandomIp()).content
        selector = html.fromstring(response)
        title = selector.xpath("//td[@id='article_content']/ul/li/a[last()]/text()")
        href = selector.xpath("//td[@id='article_content']/ul/li/a[last()]/@href")

        songlist = zip(title, href)
        global songCount

        songCount += 1
        print(num)
        saveSongList(flag[0], songlist)


def saveSongList(singer, songlist):
    global mutex
    # mutex.acquire()
    global songCountDB
    db = pymysql.connect("localhost", "root", "123456", "mypc", charset="utf8")
    cursor = db.cursor()
    for title, href in songlist:
        # ---
        title = title.replace(r"'", " ")
        sql = "insert into guitar_song(singer,title,href) values('{0}','{1}','{2}')".format(singer, title, href)
        cursor.execute(sql)
        db.commit()
        songCountDB += 1
        # print(songCountDB)
    db.close()
    # mutex.release()


def getsongInfoFromDB():
    db = pymysql.connect("localhost", "root", "123456", "mypc", charset="utf8")
    cursor = db.cursor()
    sql = "select singer,href from guitar_song where href like'%img%'"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        songInfos = cursor.fetchall()
    except:
        print("Error: unable to fetch data")

    db.close()
    return songInfos


def getSongInfoList(n, step, songInfosStrs):
    start = (n - 1) * step
    stop = (n * step)
    if stop > len(songInfosStrs):
        stop = len(songInfosStrs)
    infos = []
    for num in range(start, stop):
        flag = songInfosStrs[num - 1][1]
        singer = songInfosStrs[num - 1][0]
        url = "https://www.17jita.com/tab/" + flag
        # url = "https://www.17jita.com/" + flag[1]
        # print(url, "   -" + str(num) + "-")
        print(threading.current_thread().getName())
        print(getRandomIp())
        print(url)
        response = requests.get(url, headers=headers, proxies=getRandomIp()).content
        selector = html.fromstring(response)
        pic = selector.xpath("//td[@id='article_contents']/p/a/img/@src"
                             "|//td[@id='article_contents']/a/img/@src"
                             "|//td[@id='article_contents']/div/p/a/img/@src"
                             "|//td[@id='article_contents']/div/a/img/@src")

        try:
            title = selector.xpath("//div[@class='h hm']/h1/text()")[0]
        except:
            continue

        view = selector.xpath("//em[@id='_viewnum']/text()")[0]
        # 将图片地址拼接  XX**XX**XX
        pics = ""
        for p in pic:
            pics = pics + "**" + p
        pics = pics.lstrip("**")
        infos.append((singer, title, pics, view))
        time.sleep(1)

    saveSongInfoList(infos)


def saveSongInfoList(infos):
    print("____________________")
    db = pymysql.connect("localhost", "root", "123456", "mypc", charset="utf8")
    cursor = db.cursor()
    for info in infos:
        singer, title, pic, view = info
        title = title.replace(r"'", " ")
        sql = "insert into guitar_songinfo(singer,title,view,pic) values('{0}','{1}','{2}','{3}')".format(singer, title,
                                                                                                          view, pic)
        cursor.execute(sql)
        db.commit()
    db.close()


# 处理href字符串---whole_2233.html
def makeHrefStr():
    SuccessedHref = []
    songInfos = getsongInfoFromDB()
    for s, h in songInfos:
        tmp = h
        tmp = tmp.split("/")
        html = tmp[2].split(".")
        if bool(re.match(my_re, html[0])):
            continue
        str = "whole_" + html[0] + ".html"
        SuccessedHref.append((s, str))
    return SuccessedHref


def getSingerThread():
    # 写一个独立的函数，用来以后调用  随机ip
    singerThreads = []
    for t in range(1, getSingerPageCount() + 1):
        singerThreads.append(threading.Thread(target=getSingerlist, args=(t,)))
    for t in singerThreads:
        t.start()
    for t in singerThreads:
        t.join()


def getSongThread():
    songThreads = []
    threadCount = 20
    singerInfos = getSingerInfoFromDB()
    step = len(singerInfos) // threadCount + 1
    # 生成20个线程
    for t in range(1, threadCount + 1):
        songThreads.append(threading.Thread(target=getSongList, args=(t, step, singerInfos)))
    for t in songThreads:
        t.start()
    for t in songThreads:
        t.join()


def getSongInfoThread():
    songInfoThread = []
    threadCount = 15
    songInfosStrs = makeHrefStr()
    step = len(songInfosStrs) // threadCount + 1
    # 生成20个线程
    for t in range(1, threadCount + 1):
        songInfoThread.append(threading.Thread(target=getSongInfoList, args=(t, step, songInfosStrs)))
    for t in songInfoThread:
        t.start()
    for t in songInfoThread:
        t.join()


def main():
    global ipslist, singerCount, mutex
    singerCount = 0
    mutex = threading.Lock()

    work = input("请输入工作：（1.获取歌手列表）（2.获取歌手歌曲列表）（3.获取歌手歌曲图片列表）:\n")
    if work == "1":
        successIp = getSuccessdeIp()
        ipslist = list(successIp.items())
        getSingerThread()
    elif work == "2":
        successIp = getSuccessdeIp()
        ipslist = list(successIp.items())
        getSongThread()
    elif work == "3":
        successIp = getSuccessdeIp()
        ipslist = list(successIp.items())
        getSongInfoThread()
    else:
        print("输入结果有误，请检查~")
        exit()


if __name__ == '__main__':
    start = time.clock()
    main()
    stop = time.clock()
    print(songCount)
    print(songCountDB)
    print(stop - start)




