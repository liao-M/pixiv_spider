#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import requests
import urllib
import urllib2
import os
import time
from bs4 import BeautifulSoup

def login():
    get_cookies_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
    get_post_url = "https://accounts.pixiv.net/login?return_to=http%3A%2F%2Fwww.pixiv.net%2Franking.php%3Fmode%3Ddaily&source=pc&view_type=page"
    fouce_list_url = "http://www.pixiv.net/bookmark_new_illust.php"
    page_Num = 100

    headers_base = {
        'Referer': 'https://accounts.pixiv.net/login?return_to=http%3A%2F%2Fwww.pixiv.net%2Franking.php%3Fmode%3Ddaily&source=pc&view_type=page',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }

    headers_download = {
         "Accept-Language": "zh-CN,zh;q=0.8",
         "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }

    s = requests.session()

    def get_post_key(url):
        r = s.get(url,headers=headers_base)
        content = r.text.encode("utf-8")
        pattern = re.compile('(?<=<input type="hidden" name="post_key" value=")\w*(?=">)')
        item = re.findall(pattern, content)
        if not item:
            print  "postkey is not found"
            exit()
        post_key = item[0]
        return post_key
        # print post_key

    post_key = get_post_key(get_post_url)          # 获取登录信息post_key
    login_data = ({
        'pixiv_id': '',
        'password': '',
        'captcha': '',
        'g_recaptcha_response': '',
        'post_key': str(post_key),
        'source': 'pc'
    })
    res = s.post(get_cookies_url, data=login_data)        # 获取cookies
    print res.status_code
    m_cookies = res.cookies

    Num_total = 0
    Num = 0

    # for x in range(1,int(page_Num)+1):
    #     url = fouce_list_url + '?p=' + str(x)
    #     res = s.get(url, headers= headers_base)
    #     if res == None:
    #         break
    #     page = res.text
    #     pattern_number = re.compile(r'</div></a><a href="(.*?)"><h1 class="title" title="(.*?)">.*?</h1></a>',re.S)
    #     result_number = re.findall(pattern_number, page)
    #     for item in result_number:
    #         Num_total = Num_total + 1
    #     time.sleep(4)
    #
    # Num_file = open('Number.txt','w')
    # Num_file.write(str(Num_total))

    for x in range(2,int(page_Num)+1):
        url = fouce_list_url + '?p=' + str(x)
        res = s.get(url, headers= headers_base)
        if res == None:
            break
        page = res.text
        pattern_number = re.compile(r'</div></a><a href="(.*?)"><h1 class="title" title="(.*?)">.*?</h1></a>',re.S)
        result_number = re.findall(pattern_number, page)
        for item in result_number:
            url_one = 'http://www.pixiv.net' + str(item[0])
            resp = s.get(url_one, cookies=m_cookies, headers=headers_base)
            page_picture = resp.text
            soup = BeautifulSoup(page_picture,'lxml')
            tags = soup.find_all("img", attrs={"class": "original-image"})
            for item in tags:
                Num = Num + 1
                headers_download['referer'] = url_one
                picture_url = item['data-src']
                res = urllib2.Request(picture_url, headers=headers_download)
                req = urllib2.urlopen(res)
                name =item['alt']
                picture = req.read()
                file_name = name + '.png'
                f = open(file_name, 'wb')
                f.write(picture)
                f.close()
                print 'download the picture NO.%d' %(Num)
                time.sleep(4)

login()



# 真的只能怪自己学艺不精，忘了写return，耽误了这么久的时间，也许也和我最近在看scheme有关吧
