#-*- encoding: utf-8 -*-
'''
Created on 2017-05-23 23:37:41

@author: Captain
'''
import socket
import time
import requests
from bs4 import BeautifulSoup
from time import localtime
import multiprocessing
import sqlite3
import os

import re
path = re.compile(b'txt@=(.+?)/cid@')
uid_path = re.compile(b'nn@=(.+?)/txt@')
level_path = re.compile(b'level@=([1-9][0-9]?)/egtt@')

# connect douyu server
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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
    r = requests.get("http://www.douyu.com/"+roomid)
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
    print(client.recv(1024))
    print('login succeed')

    # joingroup, default gid is -9999
    # connect database
    msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\x00'.format(roomid)
    sendmsg(msg_more)
    dbname = 'danmudata_{}_{}-{}-{}.db'.format(get_name(roomid), localtime().tm_year,
                                               localtime().tm_mon, localtime().tm_mday)
    if dbname in os.listdir('.'):
        print("Database has already created!")
        conn = sqlite3.connect(dbname)
    else:
        print("create database")
        conn = sqlite3.connect(dbname)
        conn.execute('''CREATE TABLE DANMU (level int NOT NULL, NAME CHAR(20) NOT NULL, danmu CHAR(200) NOT NULL);''')

    # insert danmu into database
    f = open('danmudata.txt', 'a')
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
                    print("lv:"+level_list[i].decode()+">>>>>>"+uid_list[i].decode()+":"+data_list[i].decode())
                    conn.execute("INSERT INTO DANMU(level,NAME,danmu) VALUES ({0},'{1}','{2}')"
                                 .format(level_list[i].decode(), uid_list[i].decode(), data_list[i].decode()))
                    conn.commit()
                except KeyboardInterrupt:
                    conn.close()
                except Exception:
                    continue


if __name__ == '__main__':
    room_id = input('please enter the room id: \n')
    p1 = multiprocessing.Process(target=start, args=(room_id,))
    p2 = multiprocessing.Process(target=keeplive)
    p1.start()
    p2.start()



