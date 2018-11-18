# 导入requests的包 用来网络请求
import requests
# 导入lxml的包  使用xPath
from lxml import html

# 浏览器的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}

def getIpFromRemote():
    # URL = "https://www.kuaidaili.com/free/inha/1/" 根据末尾的数字进行获取不同页数
    URL = "https://www.kuaidaili.com/free/inha/"
    res = requests.get(url=URL,headers=HEADERS)
    print(res.text)
getIpFromRemote()

def test():
    URL = "http://www.17jita.com/tab/singer/index.php?page=1"
    res = requests.get(url=URL, headers=HEADERS)
    # 得到网页内容
    result = res.text
    # 使用xPath进行解析 得到相应数据
    selector = html.fromstring(result)
    hrefs = selector.xpath("//div[@class='bm_c xld']/ul/li/a/@href");
    print(hrefs)
    # print(res.text)
