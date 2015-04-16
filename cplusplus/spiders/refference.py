from scrapy.spider import Spider
from scrapy.selector import Selector
from BeautifulSoup import BeautifulSoup
from scrapy.spider import Request
from scrapy import log
import os
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor  

from cplusplus.items import RefferenceItem

def get_path(url): 
    start = url.find('//')
    if (start == -1):
        return ''

    if url.find('?') != -1:
        url = url[:url.find('?')]
    if url.find('#') != -1:
        url = url[:url.find('#')]

    if url.endswith('/'):
        url += 'index.html'

    pos1 = url.find('/', start + 2)

    url = url[pos1 + 1:]

    return url

def change_path(base, href):
    temp_path = base
    if temp_path.find('/') == 0:
        temp_path = temp_path[1:]
    if href.find('/') == 0:
        href = href[1:]
    while temp_path.find('/') != -1:
        temp = temp_path[:temp_path.find('/')]
        pos2 = href.find(temp)
        if pos2 == 0:
            href = href[len(temp)+1:]
        else:
            while temp_path.find('/') != -1:
                temp_path = temp_path[temp_path.find('/') + 1:]
                href = '../' + href
            return href
        temp_path = temp_path[temp_path.find('/') + 1:]
    return href

def create_file(work_dir, file_path, soup):
    if not os.path.isdir(work_dir):
        os.mkdir(work_dir)
    os.chdir(work_dir)
    if file_path.find('/') == 0:
        file_path = file_path[1:]
    #if not file_path.endswith('/'):
    #    file_path += '/'
    i = 0
    while file_path.find('/') != -1:
        i += 1
        temp = file_path[0:file_path.find('/') + 1]
        file_path = file_path[file_path.find('/') + 1:]
        if not os.path.exists(temp):
            os.mkdir(temp)
        os.chdir(temp)
    filename = file_path[file_path.rfind('/') + 1:]
    if not (os.path.exists(filename)):
        fo = open(filename, 'wb')
        fo.write(str(soup))
        fo.close()

    while i:
        os.chdir('../')
        i -= 1
    os.chdir('../')

class CplusplusSpider(Spider):
    name = "refference"
    allowed_domains = "cplusplus.com"
    start_urls = [
            "http://www.cplusplus.com/"
            #"http://www.cplusplus.com/reference/cassert/"
            ]
    path = ''
    workdir = 'www.cplusplus.com/'

    def __init__(self):
        Spider.__init__(self)
        #log.start()

    def parse(self, response):
        self.parse_website(response)

        soup1 = BeautifulSoup(response.body)
        self.parse_loop1(soup1, response)

    def parse_website(self, response):
        item = RefferenceItem()
        self.path = get_path(response.url)
        item['url'] = self.path
        #log('start parse, url=%s', response.url, level=log.WARNING)
        soup = BeautifulSoup(response.body)
        soup = self.rewrite_path(soup)
        # loop crawl links in this page

        #item['html'] = str(soup)
        create_file(self.workdir, self.path, soup)
        #lx = SgmlLinkExtractor()  
        #urls = lx.extract_links(response)  
        #print urls, len(urls)

    def parse_loop1(self, soup, response):
        host = response.url 
        pos1 = host.find('//')
        if pos1 != -1:
            host = host[pos1 + 2:]
            pos2 = host.find('/')
            if pos2 != -1:
                host = host[:pos2]
        else:
            return

        tags = soup.findAll(href = True)
        for tag in tags:
            if tag['href'].find('http') != 0:
                url = host + tag['href']
                yield Request(url, self.parse)

        tags = soup.findAll(src = True)
        for tag in tags:
            if tag['src'].find('http') != 0:
                url = host + tag['src']
                yield Request(url, self.parse)

    def rewrite_path(self, soup):
        if not (isinstance(soup, BeautifulSoup)): 
            return 
        tags = soup.findAll(href = True)
        for tag in tags:
            tag['href'] = self.parse_href_src(tag['href'])
        tags = soup.findAll(src = True)
        for tag in tags:
            tag['src'] = self.parse_href_src(tag['src'])

        return soup

    def parse_href_src(self, href):
        try:
            if href.index('http') == 0:
                return href
        except Exception, e:
            pass
        try:
            href = href[:href.index('?')]
        except Exception, e:
            pass
        
        try:
            href = href[:href.index('#')]
        except Exception, e:
            pass
        try:
            if (href.endswith('/')):
                href += 'index.html'
        except Exception, e:
            pass
        try:
            if (href.index('/') == 0):
                href = href[1:]
        except Exception, e:
            pass
        href = change_path(self.path, href) 

        return href
