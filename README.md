# Image loder from British Museum site
Scrapy spider for massive image upload from British museum site

You can't upload all images from site after collection search, you need to click each item and then upload it by clicking the button. So this spider was created to upload multiple items at ones.

### Usage

To use spider you need Python and Scrapy to be installed (<b>Py 3.7</b>, <b>Scrapy 2.1</b> this spider was created with)

To upload all images related to Papirus of Ani:
- upload this sources to local folder 
- open terminal
- navigate to folder with sources
- run command:
```cmd
scrapy crawl bmSpider -a query="ani,papyrus"
```
