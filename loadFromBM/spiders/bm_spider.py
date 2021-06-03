import re
import scrapy
from scrapy_splash import SplashRequest
from pathlib import Path
import requests
import shutil
import json


class BmSpider(scrapy.Spider):

    name = "bmSpider"
    allowed_domains = ["www.britishmuseum.org"]
    files_folder = "Images"
    url_filter = ""
    default_headers = {
        'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'fr-FR, fr; q=0.8, ru; q=0.6, en-US; q=0.4, en; q=0.2',
        'Host': 'www.britishmuseum.org',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
    }

    def __init__(self, query='', files_folder='Images', **kwargs):
        self.files_folder = files_folder
        filter = '&'.join('keyword='+item for item in query.split(','))
        self.url_filter = filter
        url = self.generate_url(self.url_filter, 0)
        self.logger.info("-----------------------"+url)
        self.start_urls = [url]
        super().__init__(**kwargs) 
    
    @staticmethod
    def generate_url(filter, page):
        return f'https://www.britishmuseum.org/api/_search?{filter}&view=grid&sort=object_name__asc&page={page}'
    
    def start_requests(self):
        self.logger.info("-----------------------Start requests")
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, cb_kwargs={'page': 0}, headers=self.default_headers)
    
    def parse(self, response, page):
        self.logger.info("-----------------------Parse start")
        
        json_response = json.loads(response.text)
        
        hits = json_response['hits']['hits']
        
        if len(hits) == 0:
            return
        
        for hit in json_response['hits']['hits']:

            uid = list(i for i in hit['_source']['identifier'] if i['type'] == 'unique object id')[0]['value']
            item_url = f'https://www.britishmuseum.org/api/_object?id={uid}'
            
            self.logger.info(f'-----------------------found item: {uid}')
            
            yield scrapy.Request(item_url, self.parse_concrete, cb_kwargs={'item_id': uid},
                                 headers=self.default_headers)
        
        page_url = self.generate_url(self.url_filter, page+1)
        yield scrapy.Request(page_url, self.parse, cb_kwargs={'page': page+1}, headers=self.default_headers)
    
    def parse_concrete(self, response, item_id):
        self.logger.info(f'-----------------------Parse start concrete: {item_id}')
        
        json_response = json.loads(response.text)
        
        for hit in json_response['hits']['hits']:
            for item in hit['_source']['multimedia']:
            
                file_id = item['admin']['id']
                self.logger.info(f'-----------------------found sub item: {file_id}')
            
                self.load_file(file_id, item_id + '_' + file_id)
                
    def load_file(self, file_id, item_id):
        """Upload file to local folder"""

        Path(self.files_folder).mkdir(parents=True, exist_ok=True)

        r = requests.get('https://www.britishmuseum.org/api/_image-download?id=' + file_id,
                         headers=self.default_headers, stream=True)
        
        if r.status_code == 200:
            path_to_file = Path(self.files_folder) / (item_id+'.jpg')
            self.logger.info(f'-----------------------Load file: {file_id}: LOADING')
            with open(path_to_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        
            self.logger.info(f'-----------------------Load file: {file_id}: LOADED')
            
        del r
