from dataclasses import replace
import scrapy
import json
from datetime import datetime

def timeStamped(fname, fmt='%Y-%m-%d-%H-%M-%S_{fname}'):
    return datetime.now().strftime(fmt).format(fname=fname)

class CityNotebooksSpider(scrapy.Spider):

    name = 'city_notebooks'

    custom_settings = {'FEED_URI': 'results/'+timeStamped(name)+'.json',
                        'FEED_EXPORT_ENCODING' : 'utf-8'
                      }

    allowed_domains = ['www.citilink.ru']

    start_urls = ['https://www.citilink.ru/catalog/noutbuki/']

    def parse(self, response):
        data = response.xpath(
            "//div[@class='product_data__gtm-js product_data__pageevents-js  ProductCardVertical js--ProductCardInListing ProductCardVertical_normal ProductCardVertical_shadow-hover ProductCardVertical_separated']/@data-params").extract()
        data_json = [json.loads(l) for l in data]  
        for item in data_json:
            scraped_info = {
                'id': item['id'],
                'brandName': item['brandName'],
                'shortName': item['shortName'],
                'categoryId': item['categoryId'],
                'categoryName': item['categoryName'],
                'price': item['price'],
                'oldPrice': item['oldPrice'],
                'clubPrice': item['clubPrice']
             }
            yield scraped_info

        next_page = response.xpath(
            '//a[@class="js--PaginationWidget__page PaginationWidget__arrow js--PaginationWidget__arrow PaginationWidget__arrow_right"]//@href').extract_first()
        if next_page:
            print('[=====]', next_page)
            yield scrapy.Request(next_page, self.parse)
        else:
            print('----------oops--------- next_page is not found!')
