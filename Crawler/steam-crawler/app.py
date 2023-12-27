import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import os
import re

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)


class Crawler:

    def __init__(self, urls=[]):
        self.visited_urls = []
        self.not_exist_ids = []
        self.urls_to_visit = urls
        self.base_dir = 'GatheredData/Steam/'

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)


    def crawl(self, url):
        html = self.download_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        if soup.find('div', class_="apphub_AppName") is not None:
           logging.info(f'Crawling: {url}')
           game_title = soup.find('div', class_="apphub_AppName").string
           game_title = re.sub(r'[<>:"/\\|?*]', '', game_title)
           try:
             game_description_snippet = ' '.join([tag for tag in soup.find(
                 'div', class_="game_description_snippet").strings]).strip()
             game_area_description = ' '.join([tag for tag in soup.find(
                 'div', class_="game_area_description").strings]).strip()
             game_thumbnail_image_link = soup.find(
                 'div', class_="responsive_page_header_img").find('img')['src']
             
             game_thumbnail_image_link = soup.find(
                 'div', class_="responsive_page_header_img").find('img')['src']
           except:
             self.not_exist_ids.append(url)
             with open('GatheredData/steam/not_exist_ids.txt', 'a') as file:
                file.write(f'{url}\n')     
             return None

                   
           game_dir = os.path.join(self.base_dir, game_title)
           os.makedirs(game_dir, exist_ok=True)
       
           with open(os.path.join(game_dir, 'info.txt'), 'w') as f:
               f.write(f'Steam Link: {url}\n')
               f.write(f'GameTitle: {game_title}\n')
               f.write(f'GameDescriptionSnippet: {game_description_snippet}\n \n')
               f.write(f'GameAreaDescription: {game_area_description}\n \n')
               f.write(f'GameThumbnailImageLink: {game_thumbnail_image_link}\n')
       
           img_data = requests.get(game_thumbnail_image_link).content
           with open(os.path.join(game_dir, 'thumbnail.png'), 'wb') as f:
               f.write(img_data)
               
           # Extract game ID from the URL
           game_id = url.split('/app/')[1].split('/')[0]
           self.loadAndSaveReview(f'https://steamcommunity.com/app/{game_id}/reviews?browsefilter=toprated','toprated_reviews',game_dir)
           self.loadAndSaveReview(f'https://steamcommunity.com/app/{game_id}/reviews?browsefilter=mostrecent','mostrecent_reviews',game_dir)
           self.loadAndSaveReview(f'https://steamcommunity.com/app/{game_id}/negativereviews/?browsefilter=trendyear','negative_reviews',game_dir)
           self.loadAndSaveReview(f'https://steamcommunity.com/app/{game_id}/positivereviews/?browsefilter=trendyear','positive_reviews',game_dir)
           self.visited_urls.append(url)
           with open('GatheredData/steam/crawled_ids.txt', 'a') as file:
                file.write(f'{url}\n')              
        else:
             self.not_exist_ids.append(url)
             with open('GatheredData/steam/not_exist_ids.txt', 'a') as file:
                file.write(f'{url}\n')             
        # for url in self.get_linked_urls(url, html):
        #     self.add_url_to_visit(url)
    
    def loadAndSaveReview(self, url, savefileTitle, game_dir):
        reviews_url = url
        reviews_html = self.download_url(reviews_url)
        reviews_soup = BeautifulSoup(reviews_html, 'html.parser')
        reviews_content = '\n\n'.join([tag.get_text(strip=True) for tag in reviews_soup.find_all(class_="apphub_CardTextContent")])
        with open(os.path.join(game_dir, f'{savefileTitle}.txt'), 'w', encoding='utf-8') as f:
          f.write(reviews_content)
                
    def run(self):
       page_count = 1000
       #start_id = 9000
       start_id = 1940340
       visited_urls = []
       not_exist_ids = set()
   
       with open('GatheredData/steam/not_exist_ids.txt', 'r') as file:
           for line in file:
               not_exist_ids.add(int(line.strip()))
   
       for game_id in range(start_id, start_id + page_count):
           if game_id in not_exist_ids:
               continue  
   
           url = f"https://store.steampowered.com/app/{game_id}"
           try:
               self.crawl(url)
           except Exception:
               logging.exception(f'Failed to crawl: {url}')
               with open('GatheredData/steam/not_exist_ids.txt', 'a') as file:
                   file.write(f'{url}\n')
       


if __name__ == '__main__':
    Crawler().run()
