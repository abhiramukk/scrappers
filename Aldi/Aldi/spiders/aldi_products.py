import scrapy
import json

def get_price(data, id):
    for entry in data:
        if entry['ProductId'] == id:
            return entry['ListPrice'], entry['DefaultListPrice'], entry['IsOnSale']
    return "", "", ""

class AldiProductsSpider(scrapy.Spider):
    name = 'aldi_products'
    allowed_domains = ['groceries.aldi.co.uk']
    start_urls = ['https://groceries.aldi.co.uk/']

    def parse(self, response):
        categories = response.xpath('//ul//*[text()="Groceries"]/../../following-sibling::ul[@id="level2"]/li//ul[@id="level3"]/li[position() > 1]/a[1]/@href').getall()

        for category in categories[:]:
            url = 'https://groceries.aldi.co.uk/' + category.split('?')[0] + '?sortDirection=asc&page='
            yield scrapy.Request(url + "1", callback=self.parse_product)

    
    def parse_product(self, response):
        data = response.xpath('//div[@class="products-search-results"]/@data-context').get()
        data = json.loads(data)

        category = response.xpath('//li[contains(@class,"breadcrumb-item")][2]//text()').get()
        sub_category = response.xpath('//li[contains(@class,"breadcrumb-item")][3]//text()').get()

        products = data['SearchResults']
        
        prs = []
        for product in products:
            prs.append(product['ProductId'])

        payload = {"products" : prs}
        url = 'https://groceries.aldi.co.uk/api/product/calculatePrices'
        headers = {
                    'accept-language' : 'en-GB',
                    'x-requested-with': 'XMLHttpRequest',
                    'content-type': 'application/json'
                }
        yield scrapy.Request(url, method='POST', headers=headers, body=json.dumps(payload), callback=self.parse_detail, 
                                    cb_kwargs={'data' : data, 'category' : category, 'sub_category' : sub_category})


        next = response.xpath('//a[@title="Next"]/@href').get()
        if next:
            yield response.follow(next, callback=self.parse_product)

    
    def parse_detail(self, response, data, category, sub_category):
        price_data = json.loads(response.text)['ProductPrices']
        products = data['SearchResults']

        for product in products:
            price, base_price, promo = get_price(price_data, product['ProductId'])
            item = {}
            item['Product Id'] = product['ProductId']
            item['Category'] = category
            item['Sub Category'] = sub_category
            item['Product'] = product['DisplayName']
            item['Price'] = price
            item['Base Price'] = base_price
            item['On Promo'] = 'YES' if promo else 'NO'
            item['Size'] = product['SizeVolume']

            yield item
            self.logger.info(f"Scraped: {item['Product']} ({item['Product Id']})")

