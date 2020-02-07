from bs4 import BeautifulSoup
import time
import json
import pandas as pd
import requests, re
from lxml import etree
from bs4 import BeautifulSoup

# 搜尋地區的連結，以及定義連線函數
ss = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}


def list_strip(ori_list):
    for ll, content in enumerate(ori_list):
        ori_list[ll] = content.strip()
    ori_list = list(filter(None, ori_list))
    return ori_list


# 輸入搜尋頁面的網址，回傳一個包含有各部落格的標題、網址及tag內容至主程式建立部落格列表
def get_url(page_url):
    response = ss.get(page_url, headers=headers)
    res = response.json()
    blog_url_list = []
    for each_element in res['data']['feeds']:
        each_list = [each_element['title'], each_element['link'], each_element['tags']]
        print(each_element['link'])
        blog_url_list.append(each_list)
    return blog_url_list


# list中依序為標題，網址，tags
def blog_crawl(blog_url, blog_city):
    title = blog_url[0]
    tags = blog_url[2]

    response = ss.get(blog_url[1], headers=headers)
    response.encoding = 'utf-8'
    # print(response.text)
    res = etree.HTML(response.text)
    blog_type = ', '.join(list_strip(res.xpath('//*[@id="article-box"]/div/div[2]/ul/li[1]/a//text()')))  # 全站分類
    blog_pic_url = list_strip(res.xpath('//*[@id="article-content-inner"]//p//img/@src'))  # jpg
    blog_content = ''.join(list_strip(res.xpath('//*[@id="article-content-inner"]//p//text()')))  # 內文

    # print(blog_type)
    # print(blog_pic_url)
    # print(blog_content)
    df = pd.DataFrame(
        data=[{'title': title,
               'url': blog_url[1],
               'tags': tags,
               'city': blog_city,
               'blog type': blog_type,
               'pic url': blog_pic_url,
               'article content': blog_content}],
        columns=['title', 'url', 'tags', 'city', 'blog type', 'pic url', 'article content'])
    print(df)
    return df


# 主程式，經由輸入想要爬取的地區名稱確定查詢地方之後，使True用迴圈更改頁數，收集完所有網址之後發出request取得頁面資訊
def main_crawl(city):
    city_url = []
    page = 1
    # for page in range(1, total_page+1):
    while True:
        print("現在爬取第{}頁".format(page))
        page_url = 'https://www.pixnet.net/mainpage/api/tags/{}旅遊/feeds?page={}&per_page=25'.format(city, page)
        print(page_url)
        if len(get_url(page_url)) > 0:
            city_url += get_url(page_url)
        else:
            break
        page += 1

    # 收集完所有部落格網址之後，針對每一個網址提出請求，爬取所需資訊
    city_dataframe = pd.DataFrame()
    # 傳入部落格資訊進blog_crawl函數，list中依序為標題，網址，tags
    for j, blog_data_list in enumerate(city_url):
        print('------正在爬取{}地區第{}個部落格資訊，共{}個------'.format(city, j + 1, len(city_url)))
        blog_data = blog_crawl(blog_data_list, city)
        city_dataframe = city_dataframe.append(blog_data, ignore_index=True)
    print(city_dataframe)
    city_dataframe.to_csv('{}旅遊部落格.csv'.format(city), encoding='utf-8-sig')


if __name__ == "__main__":
    city_list = ['台北', '新北']
    start = time.time()
    for i, city in enumerate(city_list):
        print('------現在爬取{}的遊記!!------'.format(city_list[i]))
        main_crawl(city)
    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = spend // 3600
    minu = (spend - 3600 * hour) // 60
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花費{hour}小時{minu}分鐘{sec}秒')
