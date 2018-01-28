# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyItem(scrapy.Item):
    name = scrapy.Field()
    web_url = scrapy.Field()
    city = scrapy.Field()
    slogan = scrapy.Field()
    industry = scrapy.Field()
    description = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()    

class ManagerItem(scrapy.Item):
    manager_photo = scrapy.Field()