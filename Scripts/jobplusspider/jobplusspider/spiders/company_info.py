# -*- coding: utf-8 -*-
import scrapy
from jobplusspider.items import CompanyItem

class CompanyInfoSpider(scrapy.Spider):
    name = 'company_info'
    # allowed_domains = ['https://segmentfault.com/companies']
    start_urls = ['https://segmentfault.com/companies']

    @property
    def start_urls(self):
        return ('https://segmentfault.com/companies?page={}'.format(i) for i in range(1, 6))

    def parse(self, response):
        item = CompanyItem()
        for company in response.css('div.company-list div.row'):
            item['name'] = company.css('h4.media-heading a::text').extract_first()
            item['web_url'] = company.css('a.company-site::attr(href)').extract_first()
            item['slogan'] = company.css('p.company-desc::text').extract_first(default='像我这样的企业是没有Slogan的')
            item['city'] = company.xpath('.//li[@class="text-muted "]/span/text()').extract_first(default='火星')
            detail_url = response.urljoin(company.css('h4.media-heading a::attr(href)').extract_first())
            request = scrapy.Request(detail_url, callback=self.parse_detail)
            request.meta['item'] = item
            yield request
    
    def parse_detail(self, response):
        item = response.meta['item']
        item['industry'] = response.css('ul.list-inline li::text').re('\w+\\+?\s?\w+')
        item['description'] = response.css('div#detailBoard p::text').extract()
        item['image_urls'] = response.css('div.img-warp img::attr(src)').extract_first()
        yield item