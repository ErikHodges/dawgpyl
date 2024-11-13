#### General webscraping

If the goal is to open a live url and convert the content to markdown, use the function:

```
from ML.ELH.code.libs.common import url2md

basename = 'google_python_styleguide' # a readable filename (with no extension) that describes the webpage
url = 'https://google.github.io/styleguide/pyguide.html' # the url of the webpage to be converted to markdown

url2md(url,basename)
```

#### Step 1: Start a Scrapy Project

Create a new Scrapy project by running:

```bash
scrapy startproject google_style_guide
cd google_style_guide
```

#### Step 2: Define the Spider

Create a spider in your Scrapy project. Navigate to the `spiders` directory inside your Scrapy project and create a file named `style_guide_spider.py`.

Paste in the following Python code for the spider:

```python
import scrapy

class StyleGuideSpider(scrapy.Spider):
    name = 'python_style_guide'
    allowed_domains = ['google.github.io']
    start_urls = ['https://google.github.io/styleguide/pyguide.html']

    def parse(self, response):
        # Extract all links from the page and yield them
        for href in response.css("a::attr(href)").getall():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_page)

        # Recursively follow the links in the navigation sidebar
        for href in response.css("#nav a::attr(href)").getall():
            url = response.urljoin(href)
            # Prevent duplicating requests to already visited URLs
            if url not in self.crawler.engine.slot.scheduler:
                yield response.follow(url, self.parse)

    def parse_page(self, response):
        # This function processes individual pages to extract or perform some action
        # For demonstrative purposes, let's just yield the URL of the page
        yield {
            'url': response.url,
            'title': response.css("title::text").get()
        }
```

#### Step 3: Run the Spider

Run your spider using the following command in the terminal from the root directory of your Scrapy project (`google_style_guide`):

```bash
scrapy crawl python_style_guide -o output.json
```

This command starts the spider named `style_guide` and stores the output in `output.json` in JSON format. The output file will contain the URLs and titles of all pages under "https://developers.google.com/style".

#### Explanations:

- **`allowed_domains`** ensures that the spider doesn’t leave the specified domain.
- **`start_urls`** is the list where the crawling starts; here, it's initialized to the main page of the Google Developer Style Guide.
- **`parse`** is the default callback method called by Scrapy when a non-initial request completes. It processes the HTTP response and extracts or performs actions.
- **`parse_page`** is a custom method designed to handle content processing of each page.
