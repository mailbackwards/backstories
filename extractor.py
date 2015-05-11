from urlparse import urlparse, urljoin
import tldextract
from newspaper import Article
from bs4 import BeautifulSoup

DEFAULT_CONTENT_NODE_TYPES = ['p']

def content_nodes(elem, node_types=None):
	if node_types is None:
		node_types = DEFAULT_CONTENT_NODE_TYPES
	return elem.find_all(node_types)

def is_valid_weblink(attr):
	return attr and not attr.startswith('mailto:')

def is_inlink(target_url, src_urls):
	"""Checks the target_url domain against all possible src_urls, and returns true if there are any domain matches."""
	#print 'Checking %s' % target_url
	if not isinstance(src_urls, list):
		src_urls = [src_urls]
	if target_url.startswith('http') or target_url.startswith('//'):
		target_url_domain = get_domain(target_url)
		source_url_domains = map(lambda u: get_domain(u), src_urls)
		if not any(target_url_domain == d for d in source_url_domains):
			return False
	return True

def strip_args(url):
    """ Accepts URL as a string and strips arguments, avoiding flags """
    FLAGS = ['on.nytimes.com/public/overview', 'query.nytimes.com']

    if not any(flag in url.lower() for flag in FLAGS):
        for i in range(len(url)):
            if url[i] == "?" or url[i] == "#":
                url_str = url[:i]
                if url_str.endswith('/all/'):
                    url_str = url_str[:-4]
                return url_str
    return url

def get_domain(url):
	return tldextract.extract(url).domain

class LinkExtractor:
	"""
	Extract metadata about all the links in a news article.

	:param url: URL of article (can be none)
	:param html: html of article (if provided, it won't use the URL param)
	:param source_url: url of the article's publication, for inlink checking
	"""

	def __init__(self, url, html=None, source_url=u''):
		if url.startswith('//'):
			url = 'http://' + url
		elif source_url and not url.startswith('http'):
			url = urljoin(source_url, url)
		article = Article(url, language='en', keep_article_html=True)
		article.download(html=html)
		article.parse()
		self.extractor = article
		self.source_url = source_url

	def article_soup(self):
		soup = BeautifulSoup(self.extractor.article_html)
		return soup

	def soup(self):
		soup = BeautifulSoup(self.extractor.html)
		return soup

	def extract(self, get_meta=False):
		links = []
		article_soup = self.article_soup()
		all_nodes = content_nodes(article_soup) or [article_soup]
		wordcount = 0
		for i, n in enumerate(all_nodes):
			wordcount += len(n.text.split())
			for a in n.find_all('a', href=is_valid_weblink):
				link = strip_args(a['href'])
				if link.startswith('//'):
					link = 'http:' + link
				elif self.source_url and not link.startswith('http'):
					link = urljoin(self.source_url, link)
				links.append({
					'href': link,
					'anchor': a.get_text(),
					'inlink': is_inlink(a['href'], [self.extractor.url, self.extractor.canonical_link, self.source_url]),
					'para': i+1,
					'_raw_attrs': a.attrs
				})
		data = {
			'story_links': links,
			'wordcount': wordcount,
			'grafcount': len(all_nodes)
		}
		if get_meta:

			# Scrape manually for various sources here
			soup = self.soup()
			if 'aljazeera.com' in self.source_url:
				headline_elem = soup.find('h1', {'class': 'articleOpinion-title'}) or soup.find('h1', {'class': 'video-heading'}) or soup.find('h1', {'class': 'heading-story'})
				headline = headline_elem.getText() if headline_elem is not None else None
				lede_elem = soup.find('h2', {'class': lambda c: c.endswith('standfirst') if c else None}) or soup.find('h2', {'class': 'video-description'})
				lede = lede_elem.getText() if lede_elem is not None else None
			elif 'globalvoicesonline.org' in self.source_url:
				headline = None
				lede = None

			try:
				date = self.extractor.publish_date.strftime('%Y-%m-%d')
			except AttributeError:
				date = ''
			data.update({
				'title': self.extractor.title,
				'headline': headline,
				'lede': lede,
				'publish_date': date,
				'authors': self.extractor.authors,
				'url': self.extractor.url,
				'img_url': self.extractor.top_image,
				'text': self.extractor.text
				})
		return data
