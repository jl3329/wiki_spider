# -*- coding: utf-8 -*-

import scrapy

class WikiItem(scrapy.Item):
    page = scrapy.Field()
    path_length = scrapy.Field()