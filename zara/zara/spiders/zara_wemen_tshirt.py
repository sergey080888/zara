import scrapy


class ZaraWemenTshirtSpider(scrapy.Spider):
    name = "zara_wemen_tshirt"
    allowed_domains = ["www.zara.com"]
    start_urls = ["https://www.zara.com/kz/ru/zhenshchiny-futbolki-l1362.html?v1=2290973"]

    def parse(self, response):
        pass
