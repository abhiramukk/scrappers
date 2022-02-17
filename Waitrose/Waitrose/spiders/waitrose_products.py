from msilib.schema import ReserveCost
import scrapy
import json
from ..utils import get_payload, validate

# def get_categories(data):
#     categories = []
#     sub_categories = []
#     for k,v in data.items():
#         if 'categoryIds' in v:
#             categories.append(v['id'])
#             sub_categories.extend(v['categoryIds'])
              
#     return categories



class WaitroseProductsSpider(scrapy.Spider):
    name = 'waitrose_products'
    allowed_domains = ['www.waitrose.com']
    start_urls = ['https://www.waitrose.com/ecom/shop/browse/groceries']

    headers = {
            'authorization': 'Bearer unauthenticated'
        }

    def parse(self, response):
        start = response.text.find('__PRELOADED_STATE__ ')
        a = response.text.find('{', start)
        z = response.text.find('</script>', start)

        data = json.loads(response.text[a:z])

        categories = []

        url = 'https://www.waitrose.com/api/content-prod/v2/cms/publish/productcontent/browse/-1?clientType=WEB_APP'
        
        categories = ['10051', '10052']
        for category in categories[:]:
            yield scrapy.Request(url, method='POST', headers=self.headers, 
                                    body=json.dumps(get_payload(category, -1)),
                                    callback=self.parse_product, cb_kwargs={'start' : 0, 'category' : category})


    def parse_product(self, response, start, category):
        data = json.loads(response.text)

        products = data['componentsAndProducts']
       
        for product in products:
            if 'searchProduct' in product:
                product = product['searchProduct']
                item = {}

                item['Product ID'] = product['id']
                item['Category'] = product['categories'][0]['name']
                if len(product['categories']) > 1:
                    item['Sub Category'] = product['categories'][1]['name']

                item['Product'] = validate(product, ['name'])
                item['Size'] = validate(product, ['size'])
                item['Base Price'] = validate(product, ['currentSaleUnitPrice', 'price', 'amount'])
                item['Selling Price'] = validate(product, ['promotion', 'promotionUnitPrice', 'amount'])
                item['Promotion'] = validate(product, ['currentSaleUnitPrice', 'promotionDescription'])
                item['Brand'] = validate(product, ['brand'])
                
                yield item
                self.logger.info(f"Scraped: {item['Product']} ({item['Product ID']})")

        
        if len(products) > 0:
            url = 'https://www.waitrose.com/api/content-prod/v2/cms/publish/productcontent/browse/-1?clientType=WEB_APP'
            yield scrapy.Request(url, method='POST', headers=self.headers, 
                                    body=json.dumps(get_payload(category, start+128)),
                                    callback=self.parse_product, cb_kwargs={'start' : start+128, 'category' : category})


