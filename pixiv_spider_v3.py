#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import os
import time
import pickle
import urllib
import urllib2
import requests
import cookielib
import threading
from bs4 import BeautifulSoup

class Pixiv(object):
    def __init__(self,file_position,pixiv_id):
        self.name = ''
        self.password = ''
        self.position = file_position
        self.id= pixiv_id
        self.url = 'http://www.pixiv.net/member_illust.php?id=' + str(pixiv_id) +'&type=all&p='
        self.get_cookies_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.get_postkey_url = "https://accounts.pixiv.net/login?return_to=http%3A%2F%2Fwww.pixiv.net%2Franking.php%3Fmode%3Ddaily&source=pc&view_type=page"
        self.headers_base = {
            'Referer': 'https://accounts.pixiv.net/login?return_to=http%3A%2F%2Fwww.pixiv.net%2Franking.php%3Fmode%3Ddaily&source=pc&view_type=page',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }

        self.headers_download = {
             "Accept-Language": "zh-CN,zh;q=0.8",
             "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
        }

        self.login_data = ({
            'pixiv_id': self.name,
            'password': self.password,
            'captcha': '',
            'g_recaptcha_response': '',
            'post_key': '',
            'source': 'pc'
        })


    def login(self):
        s = requests.session()

        page = s.get(self.get_postkey_url,headers=self.headers_base)
        content = page.text.encode("utf-8")
        pattern = re.compile('(?<=<input type="hidden" name="post_key" value=")\w*(?=">)')
        item = re.findall(pattern, content)
        if not item:
            print ('postkey is not found')
            exit()
        post_key = str(item[0])

        self.login_data['post_key'] = post_key
        res = s.post(self.get_cookies_url,data=self.login_data)
        m_cookies = s.cookies
        with open ('cookie.txt', 'wb') as f:
            pickle.dump(m_cookies, f)

    class MyThread(threading.Thread):
        def __init__(self,pic_url,pic_name,headers,position):
            threading.Thread.__init__(self)
            self.url = pic_url
            self.filename = pic_name
            self.headers = headers
            self.position = position
        def run(self):
            res = urllib2.Request(self.url,headers=self.headers)
            req = urllib2.urlopen(res)
            picture = req.read()
            filename = self.position + self.filename + '.jpg'
            with open(filename, 'wb') as f:
                f.write(picture)
                f.close()

    def create_dir(self):
        pixiv_url = 'http://www.pixiv.net/member.php?id=' + str(self.id)
        res = requests.get(pixiv_url,cookies=load_cookies('cookie.txt'),headers=self.headers_base)
        if res == None:
            print ("can't open the %s page") %(pixiv_url)
            exit()
        page = res.text
        pattern = re.compile(r'<h1 class="user">(.*?)</h1>',re.S)
        result = re.findall(pattern,page)
        name = result[0]
        try:
            self.position = self.position + str(name) + '\\'
        except:
            self.position = self.position + str(self.id) + '\\'
        isExists = os.path.exists(self.position)
        if not isExists:
            os.makedirs(self.position)
            print ("文件夹创建成功")
        else:
            print ("文件夹已存在")

    def get_pic_number_list(self,url):
        number_list =[]
        res = requests.get(url,cookies=load_cookies('cookie.txt'),headers=self.headers_base)
        # print(res.status_code)
        if res == None:
            print ("can't open the %s page" %(url))
            exit()
        page = res.text
        pattern_number = re.compile(r'</div></a><a href="(.*?)"><h1 class="title" title="(.*?)">.*?</h1></a>',re.S)
        result_number = re.findall(pattern_number, page)
        for item in result_number:
            url = 'http://www.pixiv.net' + str(item[0])
            number_list.append(url)
        return number_list

    def get_pic_url(self,pic_page_url):
        pic_url = []
        pic_name = []
        res = requests.get(pic_page_url,cookies=load_cookies('cookie.txt'),headers=self.headers_base)
        pic_page = res.text
        soup = BeautifulSoup(pic_page,"lxml")
        tags = soup.find_all("img", attrs={"class": "original-image"})
        if tags:                                                        #若是单图
            for item in tags:
                pic_url.append(item['data-src'])
                pic_name.append(item['alt'])
        else:                                                           #处理多图
            pic_mul_url = pic_page_url.replace('medium&amp;', 'manga&')
            res_mul = requests.get(pic_mul_url,cookies=load_cookies('cookie.txt'),headers=self.headers_base)    #转跳后的链接
            pic_mul_page = res_mul.text

            name_pattern = re.compile(r'<a href="/member_illust\.php\?mode=medium.*?">(.*?)</a>',re.S)
            name_result = re.findall(name_pattern,pic_mul_page)                                                 #匹配作品名字

            soup_mul = BeautifulSoup(pic_mul_page,"lxml")
            tags_mul = soup_mul.find_all("img", attrs={"class": "image ui-scroll-view"})                        #匹配图片链接
            n = 0
            for item in tags_mul:
                pic_url.append(item['data-src'])
                pic_name.append(name_result[0])
                n = n + 1
        return pic_url,pic_name


    def download_pic(self,pic_page_url):
        pic_url, pic_name = self.get_pic_url(pic_page_url)
        n = 0
        download_name = []
        for item in pic_url:
            self.headers_download['referer'] = pic_page_url
            name = pic_name[0] + str(n)
            n =  n + 1
            mt = self.MyThread(item,name,self.headers_download,self.position)
            mt.start()
            download_name.append(name)
        return download_name


def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

Num = 0
print ("please enter the pixiv number")
pixiv_id = raw_input()
print ("downloading......")
file_position = 'C:\\Users\liao\\Pictures\\'
pixiv = Pixiv(file_position,pixiv_id)
pixiv.login()
pixiv.create_dir()

for n in range(1,8):
    focus_url = pixiv.url + str(n)
    pic_number_list = pixiv.get_pic_number_list(focus_url)
    for item in pic_number_list:
        filename_list = pixiv.download_pic(item)
        for items in filename_list:
            Num = Num + 1
            print (items + 'the NO.%d   page%d')  %(Num,n)
