#web_vul_scan
web漏洞扫描器
基于爬虫的多线程web漏洞扫描器
    
    python run.py --help
    Usage: run.py [options]
    
    Options:
      -h, --help            show this help message and exit
      -d DOMAIN, --domain=DOMAIN
                            Start the domain name
      -t THREAD_NUM, --thread=THREAD_NUM
                            Numbers of threads
      --depth=DEPTH         Crawling dept
      --module=MODULE       vulnerability module(sql,xss,rfi)
      --policy=POLICY       Scan vulnerability when crawling: 0,Scan vulnerability
                            after crawling: 1
      --log=LOGFILE_NAME    save log file

支持多线程，爬虫深度，漏洞模块设置。
目前写好了sql注入，xss，文件包含三个模块。
误报漏洞还比较多。等待后续优化。

##有问题反馈
在使用中有任何问题，欢迎反馈给我，可以用以下联系方式跟我交流

* 邮件：dedwod@qq.com
* QQ: 641199800
