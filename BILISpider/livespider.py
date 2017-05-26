#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2017-05-26 14:20
@Author: Captain
"""
import time
import requests
import json

room_id = str(input('Please enter the roomid: \n'))
with open('data/live_%s.txt' % room_id, 'a') as f:
    while True:
        url = 'http://live.bilibili.com/ajax/msg'
        form = {'roomid': room_id}
        data = requests.post(url, data=form)
        heheda = json.loads(data.text, encoding='utf-8')
        for i in heheda['data']['room']:
            f.write(i['nickname']+":"+i['text']+"\n")

        time.sleep(1)



