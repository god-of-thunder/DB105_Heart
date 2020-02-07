import requests
from bs4 import BeautifulSoup
import json
from lxml import etree  # 欲使用 Xpath
from random import randint
from time import sleep
import time
import pymongo

# 設定資料庫，host填入ip
client = pymongo.MongoClient(host='192.168.243.130', port=27017)
# 指定要使用的資料庫
db = client.python_heart
# 指定要使用的collections
collection = db.Gina


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

# -----------------------
# 從url可得知輸入關鍵字可得到多少頁(page)，per_page:表示該頁可以取得25篇文章
url = 'https://www.pixnet.net/mainpage/api/tags/宜蘭旅遊/feeds?page=1&per_page=25' # json格式(第一頁共25篇)
ss = requests.session()
response = ss.get(url, headers=headers)
res = response.json()
# 從url可以得知 該關鍵字共有多少page (total_page)
total_page = res['data']['total_page']
# --------------------------------

for i in range(1, total_page):

    #     total_page = str(i)
    each_url = 'https://www.pixnet.net/mainpage/api/tags/宜蘭旅遊/feeds?page=' + str(i) + '&per_page=25'

    ss = requests.session()
    response = ss.get(each_url, headers=headers)
    print(response) #只顯示一次25篇的response
    #     time.sleep(random.randint(2,6))
    res = response.json()

    for each_element in res['data']['feeds']:
        title = []
        urll = []
        # tagss = []
        blogg = []
        # jpgg = []
        articlee = []
        dict_0 = {}


        title.append(each_element['title'])
        print('title : ', each_element['title'])

        new_url = each_element['link']
        urll.append(new_url)
        print('網址 : ', new_url)

        #         print('圖檔 : ',each_element['images_url'])  #每篇最多3張圖片

        # tagss.append(each_element['tags'])
        print('tags : ', each_element['tags'])  # 不包含搜尋的關鍵字: 台北

    # 解決請求速度過快導致程序報錯

        try:
            # 針對列表的文章進行文字的爬取
            response1 = ss.get(new_url, headers=headers)
            print(response1)
            if response1.status_code == 403:
                dict_0 = dict(title=title, url=urll, tags=each_element['tags'], blog='', jpg='', article='')

                print(dict_0)
                result = collection.insert(dict_0)
                print(result)

            else:

                #         time.sleep(random.randint(3,8))
                response1.encoding = 'utf-8'


                # 使用xpath解析網頁
                new_res = etree.HTML(response1.text)

                content_01 = new_res.xpath('//*[@id="article-box"]/div/div[2]/ul/li[1]/a//text()')  # 全站分類

                content_00 = new_res.xpath('//*[@id="article-content-inner"]//p//img/@src')  # jpg

                #         //*[@id="article-content-inner"]/p//img//@src
                content = new_res.xpath('//*[@id="article-content-inner"]//p//text()')  # 內文

                # 每篇的: 全站分類
                for j, text22 in enumerate(content_01):
                    content_01[j] = text22.strip()

                T = ''.join(content_01)
                blogg.append(T)
                print(T)

                # 每篇的jpg
                for j, text22 in enumerate(content_00):
                    content_00[j] = text22.strip()

                J = content_00
                # jpgg.append(J)
                print(J)

                # 簡單的資料清洗 (print出內文)
                for j, text22 in enumerate(content):
                    content[j] = text22.strip()

                article = ''.join(content)
                articlee.append(article)
                print(article)


                dict_0 = dict(title=title, url=urll, tags=each_element['tags'], blog=blogg, jpg=J, article=articlee)
                print('--------------------------------')
                print(dict_0)
                result = collection.insert(dict_0)
                print(result)
                print('=====================================================')


        # 第一頁    換頁         內文
        # get       json        get
        # json      json        get


        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
