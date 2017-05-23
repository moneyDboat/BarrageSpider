#-*- encoding: utf-8 -*-
'''
Created on 2017-05-23 19:20:52

@author: Captain
'''

import sys
import codecs
import jieba
from textrank4zh import TextRank4Keyword, TextRank4Sentence

text = ' '
with open('pure.txt', 'r') as f:
	for line in f.readlines():
		line = line.strip('\n')
		text += '/'.join(jieba.cut(line))
		text += ' '


# text = codecs.open('pure.txt', 'r', 'utf-8').read()
tr4w = TextRank4Keyword()
tr4w.analyze(text=text, lower=True, window=2)

print( '关键词：' )
for item in tr4w.get_keywords(20, word_min_len=1):
    print(item.word, item.weight)

print()
print( '关键短语：' )
for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2):
    print(phrase)

tr4s = TextRank4Sentence()
tr4s.analyze(text=text, lower=True, source = 'all_filters')

print( '摘要：' )
for item in tr4s.get_key_sentences(num=3):
    print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
