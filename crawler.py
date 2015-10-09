import logging
import socket
import urllib.robotparser as robotparser
from urllib.parse import urlsplit, urljoin, urldefrag
from collections import deque

import requests
from pyquery import PyQuery as pq


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance


class Page():

    def __init__(self, url):
        self.url = url
        self.url_content = None
        self.can_index = True
        self.can_follow = True

    def add_url_content(self, url_content):
        self.url_content = url_content


@singleton
class URLManager():

    def __init__(self):
        self.queued_urls = deque([])
        self.seen_urls = set()

    def init_queued_urls(self, urls):
        self.queued_urls = urls

    def add_to_queued_urls(self, new_urls):
        self.queued_urls.extend(new_urls)

    def add_to_seen_urls(self, url):
        self.seen_urls.add(url)

    def has_next_queued_url(self):
        return bool(self.queued_urls)

    def next_queued_url(self):
        return self.queued_urls.popleft()

    def seen(self, url):
        return url in self.seen_urls


class Crawler():

    def __init__(self):
        Dispatcher('seed')


class Dispatcher():

    def __init__(self, urls_file_name):
        URLManager().init_queued_urls(self.get_urls(urls_file_name))
        self.threads = 8
        self.dispatch()

    def dispatch(self):
        # TODO threads
        Fetcher()

    def get_urls(self, urls_file_name):
        initial_urls = deque([])
        with open(urls_file_name) as f:
            initial_urls.extend(f.read().splitlines())
        return initial_urls


class Fetcher():

    def __init__(self):
        self.run()

    def run(self):
        logging.info('RUN Fetcher RUN!!!')
        while URLManager().has_next_queued_url():
            print(str(len(URLManager().queued_urls)) + ' queued_urls remaining')
            url = URLManager().next_queued_url()
            url_dns = DNSCache().get_dns(url)
            if not URLManager().seen(url) and url_dns.can_fetch:
                self.fetch(url)

    def fetch(self, url):
        logging.info('Fetching url ' + url + ' ...')
        page = self.get_html_page(url)
        URLManager().add_to_seen_urls(url)
        print(str(len(URLManager().seen_urls)) + ' pages seen')
        Parser(page)
        if page.can_index:
            self.save_url_content(page)

    def get_html_page(self, url):
        page = Page(url)
        url_content = requests.get(url).text
        page.add_url_content(url_content)
        return page

    def save_url_content(self, page):
        # TODO insert in db
        url = urlsplit(page.url)
        urlFileName = (url.hostname + url.path).replace('/', '').replace('.', '')
        f = open('fetchedPages/' + urlFileName + '.html', 'wb')
        f.write(page.url_content.encode('utf-8'))
        f.close()


class Parser():

    def __init__(self, page):
        self.page = page
        self.parse()

    def parse(self):
        self.check_header()
        if self.page.can_follow:
            hyperlinks = self.get_hyperlinks()
            print('' + str(len(hyperlinks)) + ' links added to queued_urls')
            URLManager().add_to_queued_urls(hyperlinks)

    def check_header(self):
        meta = pq(self.page.url_content)('meta[name="robots"]')  # checks the meta tag robots
        if meta:
            print(meta)
            print(meta.attrib['content'])
            metaContent = (meta.attrib['content'].text).upper()
            if 'NOINDEX' in metaContent:
                page.can_index = False
            if 'NOFOLLOW' in metaContent:
                page.can_follow = False

    def get_hyperlinks(self):
        hyperlinks = set()
        anchors = pq(self.page.url_content)('a')
        # for every href in the page, clean the urls and put in a list
        for a in anchors:
            if 'href' in a.attrib:
                hyperlinks.add(self.clean_url(a.attrib['href']))
        return hyperlinks

    def clean_url(self, hyperlink):
        if self.is_absolute(hyperlink):
            href_url = urlsplit(hyperlink).geturl()
        else:
            href_url = urldefrag(urlsplit(urljoin(self.page.url, hyperlink)).geturl()).url
        return href_url

    def is_absolute(self, hyperlink):
        return bool(urlsplit(hyperlink).netloc)


@singleton
class DNSCache():

    def __init__(self):
        self.knownDNS = {}

    def get_dns(self, url):
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
        self.ip = self.get_ip(url)
        self.can_fetch = self.get_robot(url)
        logging.info(url + '[ IP:' + self.ip +
                     ', can_fetch: ' + str(self.can_fetch) + ']')

    def get_ip(self, url):
        hostname = urlsplit(url).hostname
        return socket.gethostbyname(hostname)

    def get_robot(self, url):
        rp = robotparser.RobotFileParser()
        rp.set_url(url)
        rp.read()
        return rp.can_fetch("*", url)


if __name__ == '__main__':
    logging.basicConfig(filename='log/crawler.log', level=logging.INFO)
    Crawler()
