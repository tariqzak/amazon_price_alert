================================================================================
Amazon Price Alert
================================================================================

It is a script to keep track of the changes in the price of the products.

- Python 2.6 - 2.7
- scrapy

--------------------------------------------------------------------------------
Adding/Managing Products to Scrape their Prices
--------------------------------------------------------------------------------

To add a product:

    Open the file itemDetails.json and update the json as follows :
		{"<asin>": {"price": "<Current price(Only a number, can be blank also)>", "name": "<Your product's name>", "user_mail_id": "<The email id to which you want to send the alert mail.>"}

Example:

    {"B008V6T1IW": {"price": "1643.00", "name": "Sennheiser CX 275 S In -Ear Universal Mobile Headphone With Mic (Black)", "user_mail_id": "example@gmail.com"}, "B003LPTAYI": {"price": "1699.00", "name": "Sennheiser-Professional-Over-Ear-Headphone-Black", "user_mail_id": "example2@gmail.com"}


--------------------------------------------------------------------------------
Scraping Data
--------------------------------------------------------------------------------

Go inside the scrapy project and run the following command from the command prompt.

scrapy crawl getProductPrice -a emailId=example@gmail.com -a password=password123

Here emailId is the mail id which will be used to send the mail from.


Also make sure that the email id you use to send should have permission "Access for less secure apps."
Follow this link and Turn On the feature : https://www.google.com/settings/security/lesssecureapps