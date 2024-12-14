#script to scrape tuchtrecht.overheid.nl used in
# Complaints against health professionals regarding suicidal thoughts and behaviors: a retrospective study of disciplinary law cases in The Netherlands
# Tom C. Snijders MSc, Wilco Janssen MSc, Frank L. Gerritse MD, Sisco M.P. van Veen MD PhD

import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlencode
import json

class DisciplinaryCasesSpider(scrapy.Spider):
    name = "disciplinary_cases"

    # Base URL for the disciplinary cases website
    base_url = "https://tuchtrecht.overheid.nl/Search/Search?"

    # Beroepsgroepen for the search
    beroepsgroepen = [
        "Apotheker",
        "Arts",
        "Fysiotherapeut",
        "Gezondheidszorgpsycholoog",
        "Onbekend%2Fniet-BIG+geregistreerd",
        "Psychotherapeut",
        "Tandarts",
        "Verloskundige",
        "Verpleegkundige"
    ]

    # Start date and end date for the search
    start_date = "01-01-2002"
    end_date = "01-01-2022"

    # Initialize the spider with start URLs
    def start_requests(self):
        for beroepsgroep in self.beroepsgroepen:
            params = {
                "SearchJson": json.dumps({
                    "DateFrom": self.start_date,
                    "DateTo": self.end_date,
                    "Beroep": beroepsgroep
                })
            }
            url = self.base_url + urlencode(params)
            yield scrapy.Request(url=url, callback=self.parse_search_results, meta={"beroepsgroep": beroepsgroep})

    # Parse search results to get individual case links
    def parse_search_results(self, response):
        beroepsgroep = response.meta["beroepsgroep"]
        case_links = response.css(".result-list a::attr(href)").getall()

        for link in case_links:
            yield response.follow(url=link, callback=self.parse_case_details, meta={"beroepsgroep": beroepsgroep})

        # Check for pagination and follow the next page if available
        next_page = response.css(".pagination-next a::attr(href)").get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_search_results, meta={"beroepsgroep": beroepsgroep})

    # Parse individual case details
    def parse_case_details(self, response):
        beroepsgroep = response.meta["beroepsgroep"]

        # Extract relevant case details
        case_number = response.css(".case-number::text").get()
        date_of_judgment = response.css(".judgment-date::text").get()
        summary = response.css(".summary::text").get()
        decision = response.css(".decision::text").get()

        # Save extracted data
        yield {
            "beroepsgroep": beroepsgroep,
            "case_number": case_number,
            "date_of_judgment": date_of_judgment,
            "summary": summary,
            "decision": decision,
            "source_url": response.url
        }

# Configure the Scrapy settings
process = CrawlerProcess(settings={
    "FEEDS": {
        "disciplinary_cases.json": {
            "format": "json",
            "encoding": "utf8",
            "indent": 4,
        },
    },
    "LOG_LEVEL": "INFO"
})

# Start the spider
process.crawl(DisciplinaryCasesSpider)
process.start()
