from datetime import date
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import scrapy
import json


class ZaraFinalSpider(scrapy.Spider):
    name = "zara_final"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/112.0.0.0 YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36"
    }
    start_urls = [
        "https://www.zara.com/kz/ru/category/2290973/products?ajax=true",
        "https://www.zara.com/kz/ru/category/2297813/products?ajax=true",
        # "https://www.zara.com/kz/ru/category/2105807/products?ajax=true",
    ]
    category_dict = {
        "2290973": "Женщины;Новинки;Футболки",
        "2297813": "Мужчины;Новые;Рубашки",
        # "2105807": "Женщины;Распродажа;Топы|Футболки",
    }

    def parse(self, response):
        data = json.loads(response.body)
        for i in data["productGroups"][0]["elements"]:
            if i.get("commercialComponents"):
                for new_dict in self.list_to_dict(
                    i.get("commercialComponents"), response
                ):
                    yield new_dict

    def list_to_dict(self, list_dict, response):
        new_list_dict = []

        for dict_ in list_dict:
            try:
                article = (
                    dict_["detail"]["colors"][0]["name"]
                    + "|"
                    + dict_["detail"]["displayReference"]
                )
                name = dict_["name"]
                price = float(dict_["price"] / 100)
                category_id = response.url.split("/")[-2]
                product_id = str(dict_["seo"]["discernProductId"])
                product_ditails = self.get_response1(product_id)
                url = response.urljoin(
                    urllib.parse.unquote(str(dict_["seo"]["keyword"]))
                    + "-p"
                    + str(dict_["seo"]["seoProductId"])
                    + ".html?v1="
                    + product_id
                    + "&v2="
                    + category_id
                )

                new_list_dict.append(
                    {
                        "article": article,
                        "name": name,
                        "price": price,
                        "price_old": self.old_price_(dict_),
                        "is_active": self.is_active(url),
                        "description": self.description(dict_, product_ditails),
                        "categories": self.get_category(category_id),
                        "images": self.get_images_url(product_ditails),
                        "properties": self.properties(product_id),
                        "url": url,
                        "added": str(date.today()),
                    }
                )
            except KeyError:
                print("error")

        return new_list_dict

    def is_active(self, url):
        symbol = 0
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        try:
            message = driver.find_element(
                By.CLASS_NAME, "zds-button__lines-wrapper"
            ).text

        except:
            symbol = "error"

        else:
            if message == "ДОБАВИТЬ":
                symbol = "Y"
            else:
                symbol = "N"

        driver.quit()
        return symbol

    def properties(self, product_id):
        string = ""
        url = f"https://www.zara.com/kz/ru/product/{product_id}/extra-detail?ajax=true"
        response = requests.get(url=url, headers=self.headers).text
        property_dict = json.loads(response)
        for d in property_dict:
            for a in d["components"]:
                if a.get("text"):
                    string = string + ((a.get("text").get("value")).strip()) + ";"
        return string[:-1]

    def get_category(self, category_id):
        category = self.category_dict.get(category_id)
        return category

    def get_images_url(self, data):
        images_url = ""
        mainImgs = data[0]["detail"]["colors"][0]["mainImgs"]
        for img in mainImgs:
            path = img["path"]
            name = img["name"]
            timestamp = img["timestamp"]
            base_url = (
                "https://static.zara.net/photos//"
                + path
                + "/w/416/"
                + name
                + ".jpg?ts="
                + timestamp
                + ";"
            )
            images_url = images_url + base_url
        return images_url[:-1]

    def get_response1(self, productIds):
        url = f"https://www.zara.com/kz/ru/products-details?productIds={productIds}&ajax=true"
        resp = requests.get(url=url, headers=self.headers).text
        data = json.loads(resp)
        return data

    def old_price_(self, dict_):
        old_price = dict_.get("oldPrice")
        if old_price:
            old_price = float(old_price / 100)
        return old_price

    def description(self, dict_, product_ditails):
        if dict_["description"]:
            return dict_["description"]
        else:
            return self.prepare_description(product_ditails)

    def prepare_description(self, data):
        prapared_data = data[0]["detail"]["colors"][0]["description"]
        return prapared_data
