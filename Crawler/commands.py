import os
import scrapy
from scrapy.crawler import CrawlerProcess

class SteamSpider(scrapy.Spider):
    name = 'steam_spider'
    start_urls = ['https://store.steampowered.com/app/990080/Hogwarts_Legacy/']  # Replace with the actual Steam URL you want to start with

    def parse(self, response):
        # Extract game links and yield Requests to follow them
        for href in response.css('a.app_tag::attr(href)').extract():
            yield response.follow(href, self.parse_game)

    def parse_game(self, response):
        # Extract game description
        description = response.css('div.game_description_snippet::text').extract_first().strip()
        # Extract game title or use URL to generate a filename
        title = response.css('div.apphub_AppName::text').extract_first().strip() or response.url.split('/')[-1]
        # Create directory for the game if it doesn't exist
        directory = f'GatheredData/Steam/{title}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Save the description to a text file
        with open(f'{directory}/info.txt', 'w') as f:
            f.write(f'Title: {title}\nDescription: {description}\n')

# Run the spider
process = CrawlerProcess()
process.crawl(SteamSpider)
process.start()