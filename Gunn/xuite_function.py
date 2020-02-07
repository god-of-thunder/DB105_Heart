from lxml import etree
import requests
import pandas as pd
import sys

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
headers = {'user-Agent': user_agent}


def request(url_t):
    res = requests.get(url_t, headers=headers)
    # 用etree解析網頁
    html_t = etree.HTML(res.text)
    return html_t


def article_t(html_t):
    # 印出標題
    article_title = html_t.xpath('//*[@id="element-info-title"]/text()')
    title = "".join(article_title)  # list轉string 好像可以不要,但是會有 [ ]

    # 印出內容
    article = html_t.xpath('//div[@id="element-describe-content"]')
    clear_article = article[0].xpath('string(.)').strip()  # 去空白

    lt_article = list(clear_article)  # 要list
    for k, j in enumerate(lt_article):  # enumerate(e,nu,mer,rate)枚舉
        lt_article[k] = j.strip()  # 清理前後空白
    lt_article = list(filter(None, lt_article))  # 去空值
    conotent = "".join(lt_article)

    return title, conotent


def xuite_mm(city):
    start_url = 'https://yo.xuite.net/info/search.php?keyword=' + str(city) + '&k=spot&p=1'
    url = 'https://yo.xuite.net/info/search.php?keyword=' + str(city) + '&k=spot&p='

    html = request(start_url)

    total_page = html.xpath('//p[@id="result-element-page-info"]/span[@id="result-element-page-info-total"]/text()')[0]
    # print(total_page)
    for page in range(1, int(total_page) + 1):
        next_url = url + str(page)

        html = request(next_url)
        article_link = html.xpath('//*[@id="componet-element-list"]/li/a[2]/@href')

        for link in article_link:
            each_link = 'https://yo.xuite.net' + link
            html = request(each_link)

            title, content = article_t(html)
            # print('Title:', title)
            # print('Article:', content)

            # 建立字典
            dict_t = {'Title': title, 'Article': content}
            print(dict_t)
    return


if __name__ == '__main__':
    # 要爬取的網址 台北、新北、基隆、桃園、宜蘭
    city = ['%E5%8F%B0%E5%8C%97', '%E6%96%B0%E5%8C%97', '%E6%A1%83%E5%9C%92', '%E5%AE%9C%E8%98%AD',
            '%E5%9F%BA%E9%9A%86']
    for i in city:
        xuite_mm(i)
