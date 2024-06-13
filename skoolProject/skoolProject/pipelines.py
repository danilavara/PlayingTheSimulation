# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('output.json', 'w', encoding='utf-8')  # Ensure the file is opened with UTF-8 encoding
        self.file.write('[')

    def close_spider(self, spider):
        self.file.close()
        

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + ",\n"  # Add ensure_ascii=False here
        self.file.write(line)
        return item

