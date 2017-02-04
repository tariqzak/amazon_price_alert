# -*- coding: utf-8 -*-

import scrapy
import re
from scrapy.http.request import Request
from amazon.items import AmazonItem
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import os


class AmazonProductSpider(scrapy.Spider):
    name = "getProductPrice"
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    def __init__(self,emailId,password):
        super(AmazonProductSpider, self).__init__()
        self.mailId = emailId
        self.password = password
        self.allowed_domains = ["amazon.in"]
        self.start_urls = (
            'https://www.amazon.in/',
        )
        self.current_asin = ""
        self.productDataDict = {}
        self.fileObject = ""
        self.url_scrape_count = 0
        self.scraped_product_count = 0

    def parse(self, response):
        pathToFile = os.path.join(self.__location__, 'itemDetails.json')
        os.chmod(pathToFile, 0777)
        self.fileObject = open(pathToFile, "r+")
        self.productDataDict = json.load(self.fileObject)
        for itemDetail in self.productDataDict:
            self.url_scrape_count = 0
            current_product_url = "https://www." + self.allowed_domains[0] + "/dp/" + itemDetail
            yield Request(current_product_url, callback=self.parse_page_product, meta={'asin': itemDetail})

    def parse_page_product(self, response):
        print response.meta['asin']
        asin = response.meta['asin']
        self.scraped_product_count += 1
        item = AmazonItem()
        lightning_deal_url = response.xpath("//a[@title='View Offer']/@href").extract()
        if len(lightning_deal_url) == 1:
            print lightning_deal_url[0]
            self.scraped_product_count -= 1
            lightning_deal_url = "https://www." + self.allowed_domains[0] + lightning_deal_url[0]
            yield Request(lightning_deal_url, callback=self.parse_page_product, meta={'asin': asin})
        else:
            new_response_body = response.body.partition("Deal Price:")
            if len(new_response_body[1]) == 0:
                new_response_body = response.body.partition("Sale:")
            if len(new_response_body[1]) == 0:
                new_response_body = response.body.partition("Price:")
            if len(new_response_body[1]) != 0:
                price_text = new_response_body[2].replace(",", "")
                priceRegex = re.compile(r"(?<=\>)\s*\d+\.\d+|\d+(?=\<)")
                price_match = priceRegex.search(price_text)
                if price_match:
                    price = price_match.group(0)
                    product_price = price.replace(" ", "")
                    item["name"] = self.productDataDict[asin]["name"]
                    item["price"] = product_price
                    old_price = self.productDataDict[asin]["price"]
                    if len(old_price) > 0:
                        new_price = round(float(product_price), 2)
                        old_price = round(float(old_price), 2)
                        if new_price < old_price:
                            self.send_mail(old_price, new_price, self.productDataDict[asin]["user_mail_id"], self.productDataDict[asin]["name"], response.url)
                    self.productDataDict[asin]["price"] = product_price
                    if self.scraped_product_count == len(self.productDataDict):
                        self.fileObject.seek(0)
                        self.fileObject.truncate()
                        json.dump(self.productDataDict, self.fileObject)
                        self.fileObject.close()
                    yield item
                else:
                    self.productDataDict[asin]["url"] = ""
                    if self.scraped_product_count == len(self.productDataDict):
                        self.fileObject.seek(0)
                        self.fileObject.truncate()
                        json.dump(self.productDataDict, self.fileObject)
                        self.fileObject.close()
                        print 'Failed to get the price of the product'

    def send_mail(self, old_price, new_price, mail_id, product_name, productUrl):
        current_datetime = time.asctime(time.localtime(time.time()))
        toaddrs = mail_id
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Amazon Price drop Alert!"
        msg['From'] = self.mailId
        msg['To'] = toaddrs
        msg_body = '<html><head></head><body>&nbsp;&nbsp;Your Product <b>' + product_name + '</b> price has dropped to <b>Rs.' + str(new_price) + '</b> (from Rs.' + str(old_price) + '). Hurry up...! Last checked on ' + str(current_datetime) + ' (' + time.strftime("%z", time.gmtime()) + ').<br><br><a href="' + productUrl + '">' + product_name + '</a></body></html>'
        mailContent = MIMEText(msg_body, 'html')
        msg.attach(mailContent)
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
        except smtplib.socket.gaierror:
            return False

        try:
            server.login(self.mailId,self.password)
        except SMTPAuthenticationError:
            server.quit()
            return False

        #server = smtplib.SMTP('smtp.gmail.com:587')
        #server.ehlo()
        #server.starttls()
        #server.login(self.mailId,self.password)

        try:
            server.sendmail(self.mailId, toaddrs, msg.as_string())
            return True
        except Exception:  # try to avoid catching Exception unless you have too
            return False
        finally:
            server.quit()
        #server.sendmail(self.mailId, toaddrs, msg.as_string())
        #server.quit()

