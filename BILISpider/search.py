#-*- encoding: utf-8 -*-
'''
Created on 2017-05-23 16:09:24

@author: Captain
'''

# extract relating url from search page
from bs4 import BeautifulSoup
from urllib import request
from urllib.parse import quote
import re
from bilibili import BISpider


class SearchSpider(object):
	def __init__(self):
		pass

	def get_url(self, keyword):
		url_start = 'http://search.bilibili.com/all?keyword=' + quote(keyword)
		with open('urls.txt', 'w') as f:
			for i in range(1):
				url_complete = url_start + '&page=' + str(i)
				with request.urlopen(url_complete) as req:
					data = req.read()
					soup = BeautifulSoup(data)
					elements = soup.findAll('a', class_='title')
					if elements:
						for element in elements:
							f.write('http:' + element['href'].split('?')[0])
							f.write('\n')
					else:
						break
				print('parse page ' + str(i))
		self.get_documents()

	def get_documents(self):
		bispider = BISpider()
		with open('urls.txt') as f:
			for url in f.readlines():
				bispider.set_url(url)




def main():
	keyword = '大司马班花'
	spider = SearchSpider()
	spider.get_url(keyword)
	



if __name__ == '__main__':
	main()