#coding:utf8
import requests
import re
import threading
import lxml.html
import urlparse
import time
from Queue import Queue
import sqlite3
import vul_module
import urllib2
import chardet 

from config import *


class SpiderThread(threading.Thread):
	
	def __init__(self,target,url,logfile,module):
		threading.Thread.__init__(self)
		self.target = target
		self.deep_url = url
		self.logfile = logfile
		self.module = module
		
	def GetLinks(self,host,html):
		link_list = []
		try:
			tmp = lxml.html.document_fromstring(html)
			tmp.make_links_absolute(host)
			links = tmp.iterlinks()
			link_list = list(set([i[2] for i in links]))
		except Exception, e:
			print get_ctime() + '\tXml error:',str(e)
			self.logfile.write(get_ctime() + '\tXml error:' + str(e) + '\turl:' + self.deep_url[1] +'\n')
			self.logfile.flush()
		return link_list

	def SpiderPage(self):
		link_tmp = []
		try:
			html = urllib2.urlopen(self.deep_url[1],timeout=10).read().lower()
			if chardet.detect(html)['encoding'] == 'GB2312':
				html = html.decode('gb2312').encode('utf8')
			link_list = self.GetLinks(self.target,html)
			for i in link_list:
				ext = urlparse.urlparse(i)[2].split('.')[-1]
				if ext not in IGNORE_EXT:
					link_tmp.append(i)
		except Exception,e:
			print get_ctime() + '\tHttp error:',str(e)
			self.logfile.write(get_ctime() + '\tHttp error:' + str(e) + '\turl:' + self.deep_url[1] +'\n')
			self.logfile.flush()
		link_list = link_tmp
		return link_list

	def url_similar_check(self,url):
		'''
		URL相似度分析
		当url路径和参数键值类似时，则判为重复
		'''
		global SIMILAR_SET
		url_struct = urlparse.urlparse(url)
		query_key = '|'.join(sorted([ i.split('=')[0] for i in url_struct.query.split('&') ]))
		url_hash = hash(url_struct.path + query_key)
		if url_hash not in SIMILAR_SET:
			SIMILAR_SET.add(url_hash)
			return True
		return False

	def run(self):
		global QUEUE
		global TOTAL_URL
		tmp_link_list = self.SpiderPage()
		pre_url_list = TOTAL_URL

		#判断link是否是在目标域下
		link_list = []
		for i in tmp_link_list:
			if urlparse.urlparse(self.target).netloc == urlparse.urlparse(i).netloc:
				link_list.append(i)

		TOTAL_URL = TOTAL_URL | set(link_list)
		new_url_list = list(TOTAL_URL - pre_url_list)

		#添加deep信息,并进行url相似度分析
		depth = self.deep_url[0] + 1
		for i in range(len(new_url_list)):
			if self.url_similar_check(new_url_list[i]):
				print get_ctime() + '\tCrawl url:' + new_url_list[i]
				vul_module.vul_module(new_url_list[i],self.logfile).check(self.module)
				self.logfile.write(get_ctime() + '\tCrawl url:' + new_url_list[i] + ',depth:' + str(depth) + '\n')
				self.logfile.flush()
				QUEUE.append([depth,new_url_list[i]])
