# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class WaitrosePipeline:
    def process_item(self, item, spider):
        return item

class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['Product ID'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item['Product']}")
        else:
            self.ids_seen.add(adapter['Product ID'])
            return item