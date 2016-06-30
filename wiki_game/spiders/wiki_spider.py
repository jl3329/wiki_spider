import scrapy
from wiki_game.items import WikiItem
from scrapy.selector import Selector

from urlparse import urljoin

class WikiSpider(scrapy.Spider):
    name = 'wiki'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Special:Random']

    def getNextLink(self, response):
        links = []
        for section in response.xpath('//*[@id="mw-content-text"]/p'): #p nodes in body of document
            parens_count = 0

            for node in section.xpath('node()'): #get direct children of p nodes

                for char in node.extract(): # if parens_count is 0, link is not inside parentheses
                    if char == '(': parens_count += 1
                    elif char == ')': parens_count -= 1

                #if node has href, it must follow path structure /p/a/@href
                if node.xpath('@href') and parens_count==0:
                    href = node.xpath('@href')[0].extract()
                    links.append(href)
        if not links: #Disambiguation, select first link in list not in italics
            href = response.xpath('//*[@id="mw-content-text"]/ul/li/a/@href')[0].extract()
            links.append(href)
        return links[0]

    def parse(self, response):
        title = response.xpath('//*[@id="firstHeading"]//text()').extract()
        title = ' '.join(title)

        if 'item' in response.meta:
            item = response.meta['item']
            item['path_length'] += 1
            print 'Navigated to ' + title
        else:
            item = WikiItem()
            item['page'] = title
            item['path_length'] = 1
            print 'Starting at ' + title

        if title == 'Philosophy':
            'Reached Philosophy!'
            yield item
        else:
            #italics are implemented using the <i> tag.
            #thus, all non-italicized links will follow the path structure /p/a/@href
            #while italicized links follow the path structure /p/i/a/@href

            link = self.getNextLink(response)
                        
            next_link = urljoin('http://en.wikipedia.org/', link)
            request = scrapy.Request(next_link, callback=self.parse)
            request.meta['item'] = item

            yield request

