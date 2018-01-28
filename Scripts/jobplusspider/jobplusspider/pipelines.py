# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re

from scrapy.exceptions import DropItem
from jobplusspider.items import CompanyItem, ManagerItem
import codecs
import json


class JobplusspiderPipeline(object):
    def __init__(self):
        self.company_item = set()
        
    def process_item(self, item, spider):
        if isinstance(item, CompanyItem):
            self._process_company_item(item)
        return item

    def _process_company_item(self, item):
        industry = ''
        description = ''
        if item['name'] in self.company_item:
            raise DropItem('repetion item')
        else:
            self.company_item.add(item['name'])
            for key in item['industry']:
                if re.search('雇员', key):
                    continue
                industry = key + ',' + industry 
            item['industry'] = industry
            for sentence in item['description']:
                description = sentence + description
            item['description'] = description
            with open('company_data2.json', 'a') as f:
                json.dump(dict(item), f, ensure_ascii=False)
                f.write(',\n')
            return item