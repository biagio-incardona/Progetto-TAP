import socket
import logging 
import time
import sys
import math
import subprocess
import json
import re
from datetime import datetime
from emoji import demojize

def sendLs(data, address, port):
    error = True
    while(error):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((address, port))
            sock.sendall(json.dumps(data).encode())
            sock.close()
            error = False

        except:
            print("ERROR: extract_twitch.py")
            print('Connection error. There will be a new attempt in 5 seconds')
            time.sleep(5)

def getAndSend(sock, channel, address, port):
    count = 0.0
    rate = 0.0

    start_time = time.time()
    i = 0
    while True:
        resp = sock.recv(2048).decode('utf-8')
        if resp.startswith('PING'):
            sock.send('PONG\n'.encode('utf-8'))
    
        elif len(resp) > 0:
            if i > 1:
                start = '!'
                start2 = '#'+f'{channel}'+' :'
                end = '@'
                string = demojize(resp)
                try:
                    usr = re.search('%s(.*)%s' % (start, end), string).group(1)
                    mex = re.search('%s(.*)' % start2, string).group(1)[:-1]
                    if (count%4 == 0): 
                        end_time = time.time()
                        rate = 4/(end_time-start_time)
                        start_time = end_time
 
                    json_ = {
                        'username' : usr,
                        'message' : mex,
                        'engagement' : str(rate),
                        'timestamp' : datetime.timestamp(datetime.now(tz = None)) * 1000,
                        'source' : 'twitch'
                    }
                
                    data = json_#json.loads(json_)
                    sendLs(data, address, port)
                except:
                    pass
            else:
                i = i + 1
        
        count += 1

    sock.close()

def connectToTwitch(channel):
    print('connecting to %s channel' % channel)
    oauth = 'oauth:ga1k0354tbhq3afzk7gu4ts1mnc86w'
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = 'pippo'
    
    sock = socket.socket()
    sock.settimeout(120)
    sock.connect((server, port))
    sock.send(f'PASS {oauth}\n'.encode('utf-8'))
    sock.send(f'NICK {nickname}\n'.encode('utf-8'))
    sock.send(f'JOIN #{channel}\n'.encode('utf-8'))

    print('connection established')

    return sock


channel = f'{sys.argv[1]}'
address = '10.0.100.11' #set address as string
port = 5001 #set port as int
sock = connectToTwitch(channel)
getAndSend(sock, channel, address, port)