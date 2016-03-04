#coding:utf8
from config import *
from crawl import *


def vulscan(target,thread_num,depth,module,policy,logfile):
	global QUEUE
	global TOTAL_URL

	print "[+] start scan target " + target + '...'
	logfile.write("[+] start scan target " + target + '...' + '\n') 

	QUEUE.append([0,target])
	TOTAL_URL.add(target)
	SpiderThread(target, [0,target],logfile,module).start()
	quit_flag = 0
	while(quit_flag == 0):
		while True:
			try:
				deep_url = QUEUE.pop(0)
				break
			except Exception,e:
				if threading.activeCount() == 1:
					print "[-] All crawl finish..."
					logfile.write("[-] All crawl finish..." + '\n') 
					quit_flag = 1
					break
				else:
					time.sleep(1)
					continue
		while True:
			if deep_url[0] == depth + 1:
				break
			try:
				if threading.activeCount() < thread_num:
					SpiderThread(target, deep_url,logfile,module).start()
					break
			except Exception,e:
				self.logfile.write(get_time() + '\tError:' + str(e) + '\n')
				self.logfile.flush()
				time.sleep(1)
				pass


	

