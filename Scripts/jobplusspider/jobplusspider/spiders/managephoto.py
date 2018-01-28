# -*- coding: utf-8 -*-
import scrapy
from jobplusspider.items import ManagerItem

class ManagephotoSpider(scrapy.Spider):
    name = 'managephoto'
    # allowed_domains = ['http://www.hongdagq.com/touxiang/nvsheng/']
    # start_urls = ['http://www.hongdagq.com/touxiang/nvsheng/list2.html']

    @property
    def start_urls(self):
        return ('http://www.hongdagq.com/touxiang/nvsheng/list{}.html'.format(i) for i in range(1, 15))

    def parse(self, response):
        item = ManagerItem()
        for photo in response.css('ul.list li.tx'):
            item['manager_photo'] = photo.css('img::attr(src)').extract_first() 
            yield item
