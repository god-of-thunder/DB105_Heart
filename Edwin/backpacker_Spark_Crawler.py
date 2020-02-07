from bs4 import BeautifulSoup
import time, requests, random
import re, json, os
from lxml.html.clean import Cleaner
import pymongo
from urllib import request
from datetime import datetime

def CrawlArticle(nurl, header):
    #nurl = "https://www.backpackers.com.tw/forum/showthread.php?t=10396247"
    cleaner = Cleaner(style=True, scripts=True, comments=True, javascript=True, page_structure=False,
                      safe_attrs_only=False)

    print("Debug", nurl)
    arRes = requests.get(nurl, headers=header)
    content = cleaner.clean_html(arRes.text).encode('utf-8')
    bs2 = BeautifulSoup(content, "html.parser")

    post = bs2.find("div", {"id":"posts"})
    postTable = post.select("table", {"class":"tborder"})
    content = postTable[0].select("div.vb_postbit")
    #圖片
    imgList = content[0].select("img")
    #type(imgList[0])
    imgUrl = []
    for img in imgList:
        if img.get("src") != None:
            imgUrl.append(img["src"])
        elif img.get("data-src") != None:
            imgUrl.append(img["data-src"])

    p = re.compile(r'<.*?>')
    x = p.sub("",str(content[0])).replace("\n", "")
    return x, imgUrl
    #print("1", postTable)
    #print("2", postTable[0].select("div.smallfont > strong")[0].text)
    #print("3", postTable[0].select("div.smallfont")[0].text)
    #print("4", postTable[0].select("div.vb_postbit"))

def InsertMongo(item):
    #myclient = pymongo.MongoClient("mongodb+srv://db105:b18133@cluster0-51kyj.mongodb.net/test?retryWrites=true&w=majority")
    myclient = pymongo.MongoClient("mongodb+srv://db105:b18133@cluster0-51kyj.mongodb.net/test")
    mydb = myclient["db105"]
    #mycol = mydb["BackPacker"]
    mycol = mydb["PTT"]

    #myclient = pymongo.MongoClient("mongodb://34.84.16.165:27017")
    #mydb = myclient["python_heart"]
    #mycol = mydb[colname]

    x = mycol.insert_one(item)
    #print(x)
    myclient.close()

def getImage(imgList, board="voyage"):
    imgPath =[]
    fDic = 'C:/Users/Big data/Desktop/Python/project'
    if not os.path.exists(fDic):
        os.mkdir(fDic, exist_ok=True)

    for iurl in imgList:
        time.sleep(random.randint(1, 2))
        timeStr = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        fPath = '{0}/{1}_{2}.jpg'.format(fDic, board, timeStr)
        request.urlretrieve(iurl, fPath)
        imgPath.append(fPath)

    return imgPath

def mainPage(board):
    url = "https://www.backpackers.com.tw/forum/forumdisplay.php?f=60&prefixid={0}".format(board)
    #url = "https://www.backpackers.com.tw/forum/forumdisplay.php?f=60&prefixid=voyage"
    useragnet = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    header = {'User-Agent': useragnet}
    #proxies = {"http": "http://spys.one/en/","https": "https://free-proxy-list.net/",}

    for i in range(2,3):
        res = requests.get(url, headers=header)
        cleaner = Cleaner(style=True, scripts=True, comments=True, javascript=True, page_structure=False,
                          safe_attrs_only=False)
        content = cleaner.clean_html(res.content.decode('utf-8')).encode('utf-8')
        #print(content)
        bs = BeautifulSoup(content, 'html.parser')
        body = bs.find("tbody", {"id": "threadbits_forum_60"})
        print(type(body))
        trSec = body.find_all("tr")
        print(trSec)
        artileList = []

        for tr in trSec:
            articleDict = {}
            t = tr.find_all("td", {"id": re.compile(r"^td_threadtitle_[0-9]+")})

            tdSec1 = tr.select("td", {"class": "alt1"})
            tag = tdSec1[1].select("div")
            # print(tag)
            tdSec2 = tr.select("td", {"class": "alt2", "title": "回覆"})
            # print(tdSec)
            for td in tdSec2:
                date = td.select("div.smallfont")
                if len(date) > 0:
                    #print(date[0].text.strip())
                    articleDict["date"] = date[0].text.strip().split("\n")[0]
                timer = td.select("div.smallfont > span.time")
                if len(timer) > 0:
                    #print(time[0].text.strip())
                    articleDict["time"] = timer[0].text.strip()
                user = td.select("div.smallfont > span.byx")
                if len(user) > 0:
                    #print(user[0].text.strip())
                    articleDict["author"] = user[0].text.strip()

                href = td.select("a")
                # print(href)
                for hr in href:
                    if hr["href"] != "#":
                        print("title:", hr.text)
                        if hr.text == "":
                            continue

                        articleDict["title"] = hr.text
                        articleDict["url"] = "https://www.backpackers.com.tw/forum/{0}".format(hr["href"])
                        time.sleep(random.randint(1, 5))
                        # 爬每篇文章,回傳內文跟圖片連結
                        article, imgList = CrawlArticle(articleDict["url"], header)
                        # 儲存圖片&回傳儲存路徑
                        ipath = getImage(imgList)
                        articleDict["content"] = article
                        articleDict["imgPath"] = ipath

        if len(articleDict.keys()) > 0:
            artileList.append(articleDict)

        print(artileList)
        #for a in artileList:
            #print(a)
        #    InsertMongo(a, "Backpacker")

        time.sleep(random.randint(1,5))
        url = "https://www.backpackers.com.tw/forum/forumdisplay.php?f=60&prefixid={0}&order=desc&page={1}".format(board, i)
        #url = "https://www.backpackers.com.tw/forum/forumdisplay.php?f=60&prefixid=poi&order=desc&page={0}".format(i)

if __name__ == "__main__":
    boardName = ["voyage","poi"]
    for i, b in enumerate(boardName):
        if i > 1:
            break

        mainPage(b)