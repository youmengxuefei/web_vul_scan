#coding:utf8
import os
import optparse
import time
import sys

from vulscan import *

def main():
	parser = optparse.OptionParser()  
	parser.add_option('-d','--domain',dest = 'domain',help = "Start the domain name")
	parser.add_option('-t','--thread',dest = 'thread_num',default = 100,help = "Numbers of threads")
	parser.add_option('--depth',dest = 'depth',default = 3,help = "Crawling dept")
	parser.add_option('--module',dest = 'module',default = 'all',help = "vulnerability module(sql,xss,rfi)")
	parser.add_option('--policy',dest = 'policy',default = '0',help = "Scan vulnerability when crawling: 0,Scan vulnerability after crawling: 1")
	parser.add_option('--log',dest = 'logfile_name',default='log.txt',help="save log file")

	(options, args) = parser.parse_args()

	target = options.domain
	thread_num = int(options.thread_num)
	depth = int(options.depth)
	module = options.module
	policy = int(options.policy)
	logfile_name = options.logfile_name
	logfile = open(logfile_name,'a')
	if len(sys.argv) == 1:  
		parser.error("incorrect number of arguments") 
	else:
		start_time = time.time()
		vulscan(target, thread_num, depth, module, policy, logfile)
		end_time = time.time()

		print 'running time:',end_time - start_time
	
if __name__ == '__main__':
	main()