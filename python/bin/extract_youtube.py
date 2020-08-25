import json
import socket
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
            print("ERROR: extract_youtube.py")
            print('Connection error. There will be a new attempt in 5 seconds')
            time.sleep(5)

def getAndSend(channel, address, port):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-extensions')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get("https://www.youtube.com/live_chat?v=" + channel)
    chats = []
    count = 0
    rate = 0.0
    start_time = time.time()
    while True:
        for chat in browser.find_elements_by_css_selector('yt-live-chat-text-message-renderer'):
            usr = chat.find_element_by_css_selector("#author-name").get_attribute('innerHTML')
            mex = chat.find_element_by_css_selector("#message").get_attribute('innerHTML')
            usr = str(usr).split('<')[0]

            obj = json.dumps({'author_name': usr, 'message': mex})
            x = json.loads(obj)

            if x not in chats and str(mex).find('<') == -1:
                if (count%4 == 0):
                    end_time = time.time()
                    rate = 6/(end_time-start_time)
                    if rate > 50:
                        rate = 0
                    start_time = end_time

                data = {
                    'username' : usr,
                    'message' : mex,
                    'engagement' : str(rate),
                    'timestamp' : datetime.timestamp(datetime.now(tz = None)) * 1000,
                    'source' : 'youtube'
                }
                

                chats.append(x)
                sendLs(data, address, port)

        count = count + 1

    browser.quit()

channel = "US6iyJKGNLI"
#channel = f'{sys.argv[1]}'
address = '10.0.100.11' #set address as string
port = 5002 #set port as int
getAndSend(channel, address, port)
