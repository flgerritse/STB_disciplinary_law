# scrapy runspider spider_alles.py -o resultaten.json

import scrapy
import re
import w3lib.html

beroepsgroepen =[
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

beroep_regex = r'\&beroepsgroep=([a-zA-Z*\-\+\%0-9]*)\&'

class tuchtrecht(scrapy.Spider):
    name = 'tuchtrecht_alles_2002-2021'

    def start_requests(self):
        start_urls=[]
        for beroepsgroep in beroepsgroepen:
            start_urls.append('https://tuchtrecht.overheid.nl/zoeken/resultaat?ftsscope=uitspraak&domein=Gezondheidszorg&beroepsgroep='+beroepsgroep+'&datumtype=uitspraak&datumrange=tussen&datumrangevanaf=01-01-2002&date-input--datumrangevanaf=01-01-2002&datumrangetot=01-01-2022&date-input--datumrangetot=01-01-2022')
        #start_urls = ['https://tuchtrecht.overheid.nl/zoeken/resultaat?ftsscope=uitspraak&domein=Gezondheidszorg&datumtype=uitspraak&datumrange=tot&datumtot=01-01-2020&datepicker-hidden__input--datumtot=01-01-2020%27']
        for url in start_urls:
            yield scrapy.Request(url=url, headers={"Referer":url}, callback=self.parse)
  
    def parse(self, response):
        # follow naar zaak
        for href in response.xpath('//a[@class="button button--secendary"]//@href'): #mooi ook de typefout in de layout :)
            yield response.follow(href, self.parse_zaak)

        for href in response.xpath('//li[@class="next"]//@href'):
            yield response.follow(href, self.parse)

    def parse_zaak(self, response):
        beroepsgroep = re.search(beroep_regex, str(response.request.headers.get('Referer')))
        beroepsgroep = format(beroepsgroep.group(1))

        pat = re.compile(r'\s+')
        tekst = response.xpath('//table[@class="table table--condensed table__data-overview"]//following-sibling::p//text()').extract()
        tekst = ''.join(tekst)
        tekst = tekst.replace(u'\xa0', u'')
        
        college = ""
        zaaknummer = response.xpath('//td[contains(text(),"ECLI")]//text()').extract()[0]

#college uit de ECLI halen
        if "TGZRAMS" in zaaknummer:
            college = "Amsterdam"
        elif "TGZREIN" in zaaknummer:
            college = "Eindhoven"
        elif "TGZCTG" in zaaknummer:
            college = "Centraal tuchtcollege"
        elif "TGZRSGR" in zaaknummer:
            college = "Den Haag"
        elif "TGZRZWO" in zaaknummer:
            college = "Zwolle"
        elif "TGZRGRO" in zaaknummer:
            college = "Groningen"

#zaaknummers uit de ECLI halen
        jaar = ""
        if ":2002:" in zaaknummer:
            jaar = "2002"
        elif ":2003:" in zaaknummer:
            jaar = "2003"
        elif ":2004:" in zaaknummer:
            jaar = "2004"
        elif ":2005:" in zaaknummer:
            jaar = "2005"
        elif ":2006:" in zaaknummer:
            jaar = "2006"
        elif ":2007:" in zaaknummer:
            jaar = "2007"
        elif ":2008:" in zaaknummer:
            jaar = "2008"
        elif ":2009:" in zaaknummer:
            jaar = "2009"
        elif ":2010:" in zaaknummer:
            jaar = "2010"
        elif ":2011:" in zaaknummer:
            jaar = "2011"
        elif ":2012:" in zaaknummer:
            jaar = "2012"
        elif ":2013:" in zaaknummer:
            jaar = "2013"
        elif ":2014:" in zaaknummer:
            jaar = "2014"            
        elif ":2015:" in zaaknummer:
            jaar = "2015"
        elif ":2016:" in zaaknummer:
            jaar = "2016"
        elif ":2017:" in zaaknummer:
            jaar = "2017"
        elif ":2018" in zaaknummer:
            jaar = "2018"
        elif ":2019:" in zaaknummer:
            jaar = "2019"
        elif ":2020:" in zaaknummer: #hoort geen resultaten te geven
            jaar = "2020"
        elif ":2021:" in zaaknummer: #hoort geen resultaten te geven
            jaar = "2021"

#alles samenvoegen tot de json
        yield {
            'Zaaknummer': zaaknummer,
            'College': college,
            'Jaar': jaar,
            'Datum publicatie': response.xpath('//th[contains(text(),"Datum uitspraak:")]//following-sibling::td//text()').extract(),
            'Datum uitspraak': response.xpath('//th[contains(text(),"Datum publicatie:")]//following-sibling::td//text()').extract(),
            'Beroepsgroep': beroepsgroep,
            'Onderwerp': response.xpath('//th[contains(text(),"Onderwerp:")]//following-sibling::td//text()').extract(),
            'Beslissing': response.xpath('//th[contains(text(),"Beslissingen:")]//following-sibling::td//text()').extract(),
            'Samenvatting': pat.sub(' ', response.xpath('//th[contains(text(),"Inhoudsindicatie:")]//following-sibling::td//text()').extract()[0]),
            'Volledige tekst': pat.sub(' ', w3lib.html.remove_tags(tekst)),
            'Link': response.request.url,
        }