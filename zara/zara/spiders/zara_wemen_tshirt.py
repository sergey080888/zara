import scrapy
from ..items import ZaraItem


class ZaraWemenTshirtSpider(scrapy.Spider):
    name = "zara_wemen_tshirt"
    start_urls = [
        "https://www.zara.com/kz/ru/zhenshchiny-futbolki-l1362.html?v1=2290973",
        "https://www.zara.com/kz/ru/zhenshchiny-futbolki-l1362.html?v1=2287894",
    ]

    def parse(self, response):
        items = ZaraItem()

        name = response.css("h3 ::text").extract()[1:-4]
        price = [
            (price.replace("\xa0", "")).replace(" KZT", "")
            for price in response.css(".money-amount__main ::text").extract()
        ]
        items["name"] = name
        items["price"] = price
        # items['added'] = date

        yield items
