from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re


class LidleProductsSpider(CrawlSpider):
    name = 'lidle_products'

    le1 = LinkExtractor()
    allowed_domains = ['www.lidl.co.uk']
    start_urls = ['https://www.lidl.co.uk/']


    rules = (
        Rule(LinkExtractor(), callback='parse_link', follow=True),
    )


    def parse_link(self, response):
        if '/p/' in response.url:
            title = response.xpath('//h1/text()').getall()
            title = ''.join([t.strip() for t in title])
            price = response.xpath('//article[@class="productbox"]//span[@class="pricebox__price"]/text()').get()
            if price:
                price = price.strip()

            id_1 = response.url.split('/')[-1]
            id_2 = response.xpath('//article[@class="productbox"]//img/@src').get()
            id_2 = re.findall('(article/)(.*)(/gallery)', id_2)[0][1]
            desc = response.xpath('//p[@itemprop="description"]/text()').get()
            if desc:
                desc = desc.strip()

            # promo_date = response.xpath('//article[@class="productbox"]//div[@class="ribbon__text"]/text()').get()
            base_price = response.xpath('//article[@class="productbox"]//span[@class="pricebox__recommended-retail-price"]/text()').getall()
            base_price = ''.join([t.strip() for t in base_price]).strip()


            categories = response.xpath('//div[@class="breadcrumbs__text"]/text()').getall()
            cats = categories[0] if len(categories) > 0 else ''
            # subcats = categories[1] if len(categories) > 1 else ''

            if base_price and base_price != price:
                on_promo = 'YES' 
            else:
                on_promo ='NO'
            
            yield {
                'Product ID1' : id_1,
                'Product ID2' : id_2,
                'Category' : cats,
                'Product Name' : title,
                'Price' : price,
                'Original Price' : base_price,
                'Details' : desc,
                'On Promo' : on_promo,
            }

            self.logger.info(f"Scraped: {title} ({id_1})")

        
        


