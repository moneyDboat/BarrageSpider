#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2017-05-26 11:45
@Author: Captain
"""

import socket
import time
import requests
from bs4 import BeautifulSoup
from time import localtime
import multiprocessing
import re

path = re.compile(b'txt@=(.+?)/cid@')
uid_path = re.compile(b'nn@=(.+?)/txt@')
level_path = re.compile(b'level@=([1-9][0-9]?)/sahf@')

# connect douyu server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname("openbarrage.douyutv.com")
port = 8601
client.connect((host, port))


def sendmsg(msgstr):
    # send a message to server
    msg = msgstr.encode('utf-8')
    data_length = len(msg) + 8
    code = 689
    msgHead = int.to_bytes(data_length, 4, 'little') + int.to_bytes(data_length, 4, 'little') \
                                                     + int.to_bytes(code, 4, 'little')
    client.send(msgHead)

    sent = 0
    while sent < len(msg):
        tn = client.send(msg[sent:])
        sent = sent + tn


def get_name(roomid):
    r = requests.get("http://www.douyu.com/" + roomid)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup.find('a', {'class', 'zb-name'}).string


def keeplive():
    # keep connection
    while True:
        msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\x00'
        print('Heart Beats')
        sendmsg(msg)
        time.sleep(15)


def start(roomid):
    # login
    msg = 'type@=loginreq/roomid@={}/\x00'.format(roomid)
    sendmsg(msg)
    print('login succeed')

    # joingroup, default gid is -9999
    # connect database
    msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\x00'.format(roomid)
    sendmsg(msg_more)
    txt_name = 'data/{}_{}-{}-{}.txt'.format(get_name(roomid), localtime().tm_year
                                             , localtime().tm_mon, localtime().tm_mday)

    # insert danmu into txt
    f = open(txt_name, 'a')
    print('connect {}\'s live room'.format(get_name(roomid)))
    while True:
        data = client.recv(1024)
        data_list = path.findall(data)
        uid_list = uid_path.findall(data)
        level_list = level_path.findall(data)
        if not data:
            break
        else:
            for i in range(len(data_list)):
                try:
                    level = level_list[i].decode()
                    uid = uid_list[i].decode()
                    msg = data_list[i].decode()
                    print("lv:" + level + ">>>>>>" + uid + ":" + msg)
                    f.write("%s:%s:%s" % (level, msg, uid))
                    print("%s:%s:%s" % (level, msg, uid))
                    f.write('\n')
                except KeyboardInterrupt:
                    f.close()
                except Exception as e:
                    f.write('error:' + data)
                    print(e)
                    continue


if __name__ == '__main__':
    room_id = input('please enter the room id: \n')
    p1 = multiprocessing.Process(target=start, args=(room_id,))
    p2 = multiprocessing.Process(target=keeplive)
    p1.start()
    p2.start()
