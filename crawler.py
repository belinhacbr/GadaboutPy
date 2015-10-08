import logging
import socket
import urllib.robotparser as robotparser
from urllib.parse import urlsplit

import requests


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance


@singleton
class URLManager():

    def __init__(self):
        self.queued_urls = list()  # TODO queue
        self.seen_urls = list()  # TODO hash

    def init_queued_urls(self, urls):
        self.queued_urls = urls

    def add_to_queued_urls(self, url):
        self.queued_urls.append(url)

    def add_to_seen_urls(self, url):
        self.seen_urls.append(url)

    def has_next_queued_url(self):
        return bool(self.queued_urls)

    def next_queued_url(self):
        return self.queued_urls.pop()

    def seen(self, url):
        return url in self.seen_urls


class Crawler():

    def __init__(self):
        Dispatcher('seed')


class Dispatcher():

    def __init__(self, urlsFileName):
        URLManager().init_queued_urls(self.get_urls(urlsFileName))
        self.threads = 8
        self.dispatch()

    def dispatch(self):
        Fetcher()

    def get_urls(self, urlsFileName):
        with open(urlsFileName) as f:
            initial_urls = f.read().splitlines()
        return initial_urls


class Fetcher():

    def __init__(self):
        self.run()

    def run(self):
        logging.info('RUN Fetcher RUN!!!')
        while URLManager().has_next_queued_url():
            url = URLManager().next_queued_url()
            urlDNS = DNSCache().get_dns(url)
            if not URLManager().seen(url) and urlDNS.can_fetch:
                self.fetch(url)

    def fetch(self, url):
        logging.info('Fetching url ' + url + ' ...')
        urlContent = self.get_html_page(url)
        self.save_url_content(url, urlContent)
        URLManager().add_to_seen_urls(url)
        Parser(urlContent)  # fetcher dies

    def get_html_page(self, url):
        r = requests.get(url)
        return r.text

    def save_url_content(self, url, urlContent):
        # TODO insert in db
        urlFileName = url.replace('/', '').replace(':', '').replace('\"', '').replace(
            '*', '').replace('<', '').replace('>', '').replace('|', '')
        f = open('fetchedPages/' + urlFileName + ".html", 'wb')
        f.write(urlContent.encode('utf-8'))


class Parser():

    def __init__(self, urlContent):
        self.urlContent = urlContent
        self.parse()

    def parse(self):
        if self.check_header(self.urlContent):
            hyperlinks = self.get_hyperlinks(self.urlContent)
            # queued_urls.append(hyperlinks)

    def check_header(self, urlContent):
        # TODO check if header can match the rules
        # TODO check page META ROBOTS
        # pyquery
        return False

    def get_hyperlinks(self, urlContent):
        hyperlinks = list()  # set
        # TODO
        # clean the urls
        urlHyperlink = urlsplit(url).geturl()
        hyperlinks.append()
        return hyperlinks


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
