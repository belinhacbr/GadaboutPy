import logging

#TODO PEP 0008

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class URLManager():
	def __init__(self):
		self.queued_urls = list() #TODO queue
		self.seen_urls = list() #TODO hash

	def initQueuedUrls(self, urls):
		self.queued_urls = urls

	def addToQueuedUrls(self, url):
		self.queued_urls.append(url)

	def addToSeenUrls(self, url):
		self.seen_urls.append(url)

	def hasNextQueuedURL(self):
		return bool(self.queued_urls)

	def nextQueuedURL(self):
		return self.queued_urls.pop()

	def seen(self, url):
		return url in self.seen_urls

class Crawler():
	def __init__(self):
		Dispatcher('seed')

class Dispatcher():
	def __init__(self, urlsFileName):
		URLManager().initQueuedUrls(self.getUrls(urlsFileName))
		self.threads = 8
		self.dispatch()

	def dispatch(self):
		Fetcher()

	def getUrls(self, urlsFileName):
		with open(urlsFileName) as f:
			initial_urls = f.read().splitlines()
		return initial_urls

class Fetcher():
	def __init__(self):
		self.run()
	
	def run(self):
		logging.info('RUN Fetcher RUN!!!')
		while URLManager().hasNextQueuedURL(): 
			url = URLManager().nextQueuedURL()
			urlDNS = DNSCache().getDNS(url)
			if not URLManager().seen(url) and urlDNS.can_fetch:
				self.fetch(url)

	def fetch(self, url):
		logging.info('Fetching url ' + url + ' ...')
		urlContent = self.getHTMLPage(url)
		self.saveUrlContent(url, urlContent)
		URLManager().addToSeenUrls(url)
		Parser(urlContent) #fetcher dies

	def getHTMLPage(self, url):
		import requests
		r = requests.get(url)
		return r.text

	def saveUrlContent(self, url, urlContent):
		#TODO insert in db
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

@singleton
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


if __name__ == '__main__':
	logging.basicConfig(filename='log/crawler.log', level=logging.INFO)
	Crawler()