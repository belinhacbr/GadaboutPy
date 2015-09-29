from collections import deque

class Crawler():

	def __init__(self, urlsFileName):
		self.urls = list() #queue
		self.seenUrls = list()
		self.dispatch(urlsFileName)

	def dispatch(self, urlsFileName):
		self.getSeedUrls(urlsFileName)
		self.fetch()

	def getSeedUrls(self, urlsFileName):
		#adds every url in the file to the url queue
		with open(urlsFileName) as f:
			self.urls = f.readlines()

	def fetch(self):
		while self.urls: 
			url = self.urls.pop()
			print('Fetching url ' + url + ' ...')
			urlContent = self.getHTMLPage(url)
			hyperlinks = self.getHyperlinks(urlContent)
			#self.urls.append(hyperlinks)
			self.saveUrlContent(url, urlContent)
			self.seenUrls.append(url)

	def getHTMLPage(self, url):
		#TODO resolve robots.txt
		import requests
		r = requests.get(url)
		return r.text

	def getHyperlinks(self, urlContent):
		#TODO check page robots.txt
		return list()
		
	def saveUrlContent(self, url, urlContent):
		urlFileName = url.replace('/', '').replace(':', '').replace('\"', '').replace('*', '').replace('<', '').replace('>', '').replace('|', '');
		f = open('fetchedPages/'+urlFileName+".html", 'w')
		f.write(urlContent.encode('utf-8'))

Crawler('seed')







		




		




		