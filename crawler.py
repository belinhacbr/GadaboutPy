import logging


#TODO remove global create URLManager
queued_urls = list() #TODO queue
seen_urls = list()

class Crawler():
	def __init__(self, urlsFileName):
		Dispatcher(urlsFileName)

class Dispatcher():
	def __init__(self, urlsFileName):
		global queued_urls
		queued_urls = self.getUrls(urlsFileName)
		self.threads = 8
		self.dispatch()

	def dispatch(self):
		Fetcher()

	def getUrls(self, urlsFileName):
		#adds every url in the file to the url queue
		with open(urlsFileName) as f:
			initial_urls = f.read().splitlines()
		return initial_urls

class Fetcher():
	def __init__(self):
		self.DNS_cache = DNSCache()
		logging.info('RUN Fetcher RUN!!!')
		self.run()
	
	def run(self):
		global queued_urls
		global seen_urls
		print(queued_urls)
		while queued_urls: 
			url = queued_urls.pop()
			print(seen_urls)
			if url not in seen_urls:
				urlDNS = self.DNS_cache.getDNS(url)
				if urlDNS.can_fetch:
					self.fetch(url)

	def fetch(self, url):
		global seen_urls
		logging.info('Fetching url ' + url + ' ...')
		urlContent = self.getHTMLPage(url)
		self.saveUrlContent(url, urlContent)
		seen_urls.append(url)
		Parser(urlContent) #fetcher dies

	def getHTMLPage(self, url):
		import requests
		r = requests.get(url)
		return r.text

	def saveUrlContent(self, url, urlContent):
		urlFileName = url.replace('/', '').replace(':', '').replace('\"', '').replace('*', '').replace('<', '').replace('>', '').replace('|', '');
		f = open('fetchedPages/'+urlFileName+".html", 'wb')
		f.write(urlContent.encode('utf-8'))

class Parser():
	def __init__(self, urlContent):
		self.urlContent = urlContent
		self.parse()

	def parse(self):
		if self.checkHeader(self.urlContent):
			hyperlinks = self.getHyperlinks(self.urlContent)
			#queued_urls.append(hyperlinks)

	def checkHeader(self, urlContent):
		#TODO check if header can match the rules
		#TODO check page META ROBOTS
		#pyquery
		return False


	def getHyperlinks(self, urlContent):
		hyperlinks = list() #set
		#TODO
		#clean the urls
		from urllib.parse import urlsplit
		urlHyperlink = urlsplit(url).geturl()
		hyperlinks.append()
		return hyperlinks


class DNSCache():
	def __init__(self):
		self.knownDNS = {}

	def getDNS(self, url):
		from urllib.parse import urlsplit
		host = urlsplit(url).hostname
		if host in self.knownDNS:
			logging.info('DNS cache hit for: ' + host)
			return self.knownDNS[host]
		else:
			newDNS = DNSResolver(url)
			self.knownDNS[host] = newDNS
			return newDNS

class DNSResolver():
	def __init__(self, url):
		self.ip = self.getIP(url)
		self.can_fetch = self.getRobot(url)
		logging.info(url + '[ IP:' + self.ip + ', can_fetch: '+ str(self.can_fetch) + ']')

	def getIP(self, url):
		import socket
		from urllib.parse import urlsplit
		hostname = urlsplit(url).hostname
		return socket.gethostbyname(hostname)

	def getRobot(self, url):
		import urllib.robotparser as robotparser
		rp = robotparser.RobotFileParser()
		rp.set_url(url)
		rp.read()
		return rp.can_fetch("*", url)


logging.basicConfig(filename='log/crawler.log', level=logging.INFO)
Crawler('seed')