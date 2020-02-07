from pyspark import SparkContext
import backpacker_Spark_Crawler as bsc
from bs4 import BeautifulSoup
import requests
import re, time, random, datetime
from elasticsearch import Elasticsearch

def getUrl(boardName):
    #print(__name__)
    #url = ""
    pageNum = 1203
    urlList = []
    useragnet = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    headers = {'User-Agent': useragnet}
    indexUrl = "https://www.ptt.cc/bbs/{0}/index.html".format(boardName)
    for i in range(2):
        if i == 0:
           urlList.append(indexUrl)
           #find last page number
           res = requests.get(indexUrl, headers=headers)
           soup2 = BeautifulSoup(res.text, 'html.parser')
           btnDiv = soup2.find("div", {"class": "btn-group btn-group-paging"})
           btn = btnDiv.select("a")
           nextUrl = btn[1]["href"]
           u = nextUrl.split("/")
           pageNum = int(u[-1].split(".")[0][5:]) + 1
           print(pageNum)
        else:
           urlList.append("https://www.ptt.cc/bbs/{0}/index{1}.html".format(boardName, pageNum-i))

    return urlList

def Crawl(url):
    time.sleep(random.randint(1, 5))
    contentList = []
    useragnet = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    headers = {'User-Agent': useragnet}

    res = requests.get(url, headers=headers)
    soup2 = BeautifulSoup(res.text, 'html.parser')  # requests的回傳值res要用text才能顯示
    title_bar = soup2.findAll('div', {'class': 'title'})
    for t in title_bar:
        time.sleep(random.randint(1, 5))
        contentDict = {}
        for s in t.findAll('a'):
            # print('title:', s.string)
            contentUrl = 'https://www.ptt.cc{0}'.format(s['href'])
            # print(goUrl)
            url1_res = requests.get(contentUrl, headers=headers)
            url1_soup = BeautifulSoup(url1_res.text, 'html.parser')
            main_content = url1_soup.select('div[class="bbs-screen bbs-content"]')
            o_text = main_content[0].text.split('--')  # 把本文和下方的推文分隔開
            contentDict["url"] = contentUrl
            contentDict["title"] = re.sub('[\\\\/:*?"<>|]', ' ', s.string)
            contentDict["content"] = o_text[0]
            #score = getScored(url1_soup)

            # 抓出ID,title,time
            metaLine = url1_soup.find_all('div', {'class': 'article-metaline'})
            for mline in metaLine:
                contentDict[mline.select('span')[0].text] = mline.select('span')[1].text
                #if mline.select('span')[0].text == "時間":
                #    wdate = datetime.datetime.strptime(mline.select('span')[1].text, "%a %b %d %H:%M:%S %Y")
                #    contentDict["DateTime"] = wdate

        #print(contentDict)
        return contentDict

def insertELK(doc):
    es = Elasticsearch('http://192.168.11.129:9200')
    res = es.index(index='ptt_travel', doc_type='ptt', body=doc)
    return res

if __name__ == "__main__":
    board = ["Tai-travel", "N_E_Coastal"]
    sc = SparkContext()
    url = []
    for b in board:
        url.extend(getUrl(b))

    print(url)
    #Crawl(url[0])
    #url = ["https://www.ptt.cc/bbs/Tai-travel/index.html"]
    purl = sc.parallelize(url)

    result = purl.map(Crawl).collect()
    #print(result)

    #rex = sc.parallelize(result)
    #res2 = rex.map(insertELK).collect()
    for r in result:
        bsc.InsertMongo(r)