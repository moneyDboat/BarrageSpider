# -*- encoding: utf-8 -*-
'''
Created on 2017-05-23 12:04:40
Updated on 2017-05-23 12:20:36

@author: Captain
'''

from bs4 import BeautifulSoup
from urllib import request
from io import BytesIO
import gzip
import zlib
import re
import os 
import time 
import sys
import getopt
import argparse


class BISpider(object):
    def __init__(self, output='documents', parser='lxml'):
        self.output = output
        self.xml = False
        self.parser = parser

    def gzip_url(self, url):
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip',
            'Referer': 'http://www.bilibili.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        req = request.Request(url, headers=header)
        response = request.urlopen(req)
        # gzip解压
        if response.info().get('Content-Encoding') == 'gzip':
            compresseddata = response.read()
            buf = BytesIO(compresseddata)
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        # default解压
        else:
            data = zlib.decompress(response.read(), -zlib.MAX_WBITS)
        return data

    def set_url(self, url):
        html = self.gzip_url(url)
        # f = open('data/html.txt', 'wb')
        # f.write(html)
        # f.close()
        print('视频页面 gzip解压完成...')
        print(url)

        try:
            soup = BeautifulSoup(html, self.parser)
            da1 = soup.find('div', id='bofqi')
            jsstring = da1.script.string 

            p = re.compile(r'cid=\d+&')
            cid = p.findall(jsstring)[0][4:-1]
            print('cid获取完成...')
            self.get_documents(cid)
        except Exception as e:
            print('something unexpected happened ->')
            print(e)

    def get_documents(self, cid):
        documents_url = 'http://comment.bilibili.com/' + cid + '.xml'

        data = self.gzip_url(documents_url)
        print("弹幕页面解压完成...")
        if self.xml:
            fd = open('data/' + self.output + '.xml', 'w')
            fd.write(data)
            fd.close()
            print(self.output + '.xml写入完成')

        soup = BeautifulSoup(data, self.parser)
        documents = soup.find_all('d')
        fw = open('data/' + self.output + '.txt', 'a')
        fwpure = open('data/pure.txt', 'a')

        print("写入弹幕ing...")
        for document in documents:
            content = str(document.string)

            attr = document['p'].split(',')
            t1 = str(attr[0])  # 视频中的时间
            t2 = attr[4]  # 发布时间
            timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(t2)))

            fw.write(content + '\t' + t1 + '\t' + timestr + '\n')
            fwpure.write(content + '\n')

        fw.close()
        print("写入完成...请查看%s.txt" % self.output)		


def main():
    parser = argparse.ArgumentParser(description='Welcome to BILI')
    parser.add_argument('-i', '--input', help='set the av_number to crawl')
    parser.add_argument('-o', '--output',  help='set the filename to store')
    parser.add_argument('-x', '--xml', action='store_true', help='output as xml')
    parser.add_argument('-p', '--parser', help='default use lxml parser')

    args = parser.parse_args()

    spider = BISpider()
    if args.parser:
        spider.parser = args.parser
    if args.output:
        spider.output = args.output
    if args.xml:
        spider.xml = args.xml

    print('av_number' + str(args.input))
    url = r'http://www.bilibili.com/video/av' + str(args.input)
    spider.set_url(url)


if __name__ == '__main__':
    print('haha')
    main()




