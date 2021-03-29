import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from elkhornvalleybank.items import Article


class elkhornvalleybankSpider(scrapy.Spider):
    name = 'elkhornvalleybank'
    start_urls = ['https://www.elkhornvalleybank.com/Info/News']

    def parse(self, response):
        articles = response.xpath('//div[@class="row wsc-margin-bottom-sm"]')
        for article in articles:
            link = article.xpath('.//div[@class="read_more"]/a/@href').get()
            date = article.xpath('./div[@class="col-blog col-md-1"]//text()').getall()
            date = [text for text in date if text.strip()]
            date = " ".join(date).strip()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('(//div[@class="pagination"]//li/a)[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="post_link"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="wsc_pi_body"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
