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
        description_selector = response.css('game_description_snippet')
        description = description_selector.get()
        if description:
            description = description.strip()
        else:
            description = 'No description available'
        # Extract game title or use URL to generate a filename
        title_selector = response.css('div.apphub_AppName::text')
        title = title_selector.extract_first()
        if title:
            title = title.strip()
        else:
            title = 'No title available'
        # Create directory for the game if it doesn't exist
        directory = f'GatheredData/Steam/{title}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Save the description to a text file
        with open(f'{directory}/info.txt', 'w', encoding='utf-8') as f:
            f.write(f'Title: {title}\nDescription: {description}\n')

# Run the spider
process = CrawlerProcess()
process.crawl(SteamSpider)
process.start()
