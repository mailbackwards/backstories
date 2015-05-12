import sys
from datetime import datetime
import hashlib
import networkx as nx

from extractor import LinkExtractor
from storage import MongoStoryDatabase
from conf import DBS, DEFAULT_SOURCE_URL


class LinkSpider(object):

    def __init__(self, db_name):
        db_name = db_name
        self.db = CustomStoryDatabase(db_name)
        self.hrefs = set()
        self.queue = set()

    def spider_from(self, url, source_url=None, limit=20000):
        print '%d links crawled, %d links in queue. url %s' % (len(self.hrefs), len(self.queue), url)
        if url not in self.hrefs:
            self.hrefs |= set([url])
            data = LinkExtractor(url, source_url=source_url).extract(get_meta=True)
            data.update({
                'guid': url,
                'stories_id': hashlib.md5(url).hexdigest()
            })
            story = self.db.addStory(data)
            limit -= 1
            # Add the inlinks to a queue so we get the closest links first
            self.queue |= set([link['href'] for link in data['story_links']
                              if link['inlink'] is True and link['href'] not in self.hrefs and not any((subl in link['href'] for subl in ('/topics/',)))])
        else:
            print '--> Already crawled'
        if self.queue:
            return self.spider_from(self.queue.pop(), source_url=source_url, limit=limit)
        return len(self.hrefs)

def reformat_date(datestr):
    if not datestr:
        return ''
    date_obj = datetime.strptime(datestr, '%Y-%m-%d')
    return date_obj.strftime('%B %d, %Y')

class CustomStoryDatabase(MongoStoryDatabase):

    def buildGraph(self, query=None, inlinks_only=True):
        """
        Builds a networkx graph from a list of stories.

        :param stories: iterable of Media Cloud stories.
        :param inlinks_only: set to True to prevent links from other domains from being part of the graph.
        """
        query = query or {}
        stories = self._db.stories.find(query)
        graph = nx.DiGraph()
        for story in stories:
            node = story['guid']
            graph.add_node(node, story)
            for link in story['story_links']:
                if inlinks_only is True and link['inlink'] is False:
                    continue
                linknode = link['href']
                graph.add_node(linknode)
                graph.add_edge(node, linknode, link)
        return graph

    def getSpiderRows(self, srcnode, query=None, inlinks_only=True, spider_limit='all'):
        graph = self.buildGraph(query, inlinks_only)
        results = []
        for node, data in graph.nodes_iter(data=True):
            data['path_length'] = nx.algorithms.shortest_path_length(graph, srcnode, node)
            if spider_limit != 'all' and data['path_length'] > int(spider_limit):
                continue
            data['degree'] = graph.in_degree(node)
            data['node'] = node
            data['publish_date_formatted'] = reformat_date(data.get('publish_date'))
            results.append(data)
        return results

if __name__ == "__main__":
    try:
        args = sys.argv[1:]
    except:
        print 'We need a URL'
    while len(args) < 3:
        args.append(None)
    starting_url = args[0]
    db_name = args[1] or DEFAULT_DB_NAME
    source_url = args[2] or DEFAULT_SOURCE_URL

    LinkSpider(db_name).spider_from(starting_url, source_url=source_url)
