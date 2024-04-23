import scrapy
from image_scraper.items import ImageScraperItem


class VisirSpiderSpider(scrapy.Spider):
    name = "visir_spider"
    allowed_domains = ["www.visir.is"]
    start_urls = ["https://www.visir.is"]

    def parse(self, response):

        images = response.css('img[alt="Fréttamynd"]')

        image_urls = []
        for img in images:
            url = img.attrib['src']
            if not url.startswith(self.start_urls[0]):
                url = self.start_urls[0] + url

            image_urls.append(url)

        yield ImageScraperItem(image_urls=image_urls)
