from lxml import etree
import requests
import pymongo
import pandas as pd

# # 設定資料庫，host填入ip
# client = pymongo.MongoClient(host='34.84.16.165', port=27017)
# # 指定要使用的資料庫
# db = client.python_heart
# # 指定要使用的collections
# collection = db.Gunn

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
headers = {'user-Agent': user_agent}

# 要爬取的網址 台北、新北、基隆、桃園、宜蘭
city = ['%E5%8F%B0%E5%8C%97', '%E6%96%B0%E5%8C%97', '%E6%A1%83%E5%9C%92', '%E5%AE%9C%E8%98%AD', '%E5%9F%BA%E9%9A%86']

Title = []
Article = []
for i in city:
    start_url = 'https://yo.xuite.net/info/search.php?keyword=' + str(i) + '&k=spot&p=1'
    url = 'https://yo.xuite.net/info/search.php?keyword=' + str(i) + '&k=spot&p='

    res = requests.get(start_url, headers=headers)
    # 用etree解析網頁
    html = etree.HTML(res.text)
    # xpath抓取總頁數
    total_page = html.xpath('//p[@id="result-element-page-info"]/span[@id="result-element-page-info-total"]/text()')[0]
    # print(total_page)
    for page in range(1, int(total_page) + 1):
        next_url = url + str(page)
        # print(next_url)
        res = requests.get(next_url, headers=headers)
        html = etree.HTML(res.text)
        # 用xpath抓取每一個文章的網址
        article_link = html.xpath('//*[@id="componet-element-list"]/li/a[2]/@href')
        # print(article_link)
        for link in article_link:
            each_link = 'https://yo.xuite.net' + link
            # print(each_link)
            res1 = requests.get(each_link, headers=headers)
            # 解析成xpath語法
            html = etree.HTML(res1.text)

            # 印出文章題目
            article_title = html.xpath('//*[@id="element-info-title"]/text()')
            title1 = "".join(article_title)  # list轉string 好像可以不要,但是會有 [ ]
            print('Title:', title1)

            # 印出文章內文
            article = html.xpath('//div[@id="element-describe-content"]')
            clear_article = article[0].xpath('string(.)').strip()  # 去空白
            # print('Article:', clear_article)
            # print(type(clear_article))

            lt_article = list(clear_article)  # 要list
            for k, j in enumerate(lt_article):  # enumerate(e,nu,mer,rate)枚舉
                lt_article[k] = j.strip()  # 清理前後空白
            lt_article = list(filter(None, lt_article))  # 去空值
            str_article = "".join(lt_article)  # list轉str
            print('Article:', str_article)

            # 建立字典
            # dict = {'Title': title1, 'Article': str_article}
            # print(dict)

            # 輸出至資料庫
            # result = collection.insert(dict)
            # print(result)

            print('-' * 50 + str(page) + '-' * 50)

            Title.append(title1)
            Article.append(str_article)

# print(Title)
# print(Article)

# 存成DataFrame
df = pd.DataFrame({'Title': Title, 'Article': Article})  # 建立欄位及輸入
# print(df)

# 存成json
# df.to_json('E:/PycharmProjects/work/xuite_spider.js', orient='records', force_ascii=False)  # records設定格式,force設定輸出不亂碼

# 存成csv
# df.to_csv('D:/PycharmProjects/work/xuite_spider.csv', index=0, encoding='utf-8-sig')  # 輸出
