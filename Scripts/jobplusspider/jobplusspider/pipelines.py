# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from jobplusspider.items import CompanyItem, ManagerItem
import codecs
import json


class JobplusspiderPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, CompanyItem):
            self._process_company_item(item)
        else:
            self._process_manager_item(item)
        return item

    def _process_company_item(self, item):
        industry = ''
        description = ''
        for key in item['industry']:
            industry = industry + ',' + key
        item['industry'] = industry
        for sentence in item['description']:
            description = sentence + description
        item['description'] = description
        with open('company_data.json', 'a') as f:
            json.dump(dict(item), f, ensure_ascii=False)
            f.write(',\n')
        return item
    
    def _process_manager_item(self, item):
        with open('manager_data.json', 'a') as f:
            json.dump(dict(item), f, ensure_ascii=False)
            f.write(',\n')
        return item


