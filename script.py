# -*- coding: utf-8 -*-

# Gmail Imports (not important for the actual crawler)
from SendGmailSimplified.SendGmailSimplified import SimplifiedGmailApi

# My imports (the crawler)
import json
import os
from bs4 import BeautifulSoup
import httplib2
import logging
import requests
import re

# Paths for important directories and files - from home directory
HOME_DIR = os.path.expanduser('~')

# change this to the directory your script is: !!!!!!!!!!!!!!!!!
DIR_OF_SCRIPT = os.path.join(HOME_DIR, os.path.join("Documents", "NewYearPlanNotifierAEG"))
# Documents
# Documents/GitHubBeta
# PycharmProjects

PATH_FOR_LOG = os.path.join(DIR_OF_SCRIPT, "script.log")
PATH_OF_DATA_FILE = os.path.join(DIR_OF_SCRIPT, 'data.json')
PATH_OF_HTML_FILE = os.path.join(DIR_OF_SCRIPT, 'data.html')

logging.basicConfig(filename=PATH_FOR_LOG, level=logging.DEBUG)

# Setup the Gmail API - set USE_GMAIL False if you want to use the Simplified Gmail API
USE_GMAIL = False

if USE_GMAIL:
    URL_OF_WEBSITE = "http://www.aeg-boeblingen.de/index.php/aktuelles/stundenplan"
    RECIPIENTS = ["yourEmailAdress@sonstwas.com", "onemore@gmail.com"]

# get website content by using a Cookie
try:
    logging.info("Try getting the website " + URL_OF_WEBSITE + ":")
    http = httplib2.Http()
    headers = {'Cookie': "6024a7383aa153ec184c3ea3382596a7=lnkevh32t64d684tkpa1nkra54"}
    response, content = http.request(URL_OF_WEBSITE, 'GET', headers=headers)
except requests.HTTPError as err:
    logging.warning(err)
except requests.ConnectionError as err:
    logging.warning(err)
else:
    logging.info("Process was successful.")

    # Now crawl the information from the website:
    soup = BeautifulSoup(content, 'html.parser')
    # get all div's with the class custom
    soup = soup.find_all('div', {'class': 'custom'})[1]
    # took the second one and get the p tag from it as a String
    soup = str(soup)
    # replace all extra lines (\n) with nothing
    soup = soup.replace("\n", "")
    # repair all the links so that they are usable
    soup = soup.replace("href=\"/", "href=\"http://www.aeg-boeblingen.de/")

    # Load the old file information if it exists
    if os.path.isfile(PATH_OF_DATA_FILE):
        with open(PATH_OF_DATA_FILE) as data_file:
            data = json.load(data_file)

        # Convert the data into JSON format if old data exists
        jsonData = json.dumps(soup)
        jsonData = json.loads(jsonData)
    else:
        data, jsonData = None, None

    # Check if the old file is different from the current information
    if data is None or jsonData != data:

        # If yes send a HTML email to all recipients
        if USE_GMAIL:
            
            # algorithm encoding source: http://code.activestate.com/recipes/251871-latin1-to-ascii-the-unicode-hammer/
            xlate = {0xdf: '&#223;', # ß
                     0xc4: '&#196;', # Ä
                     0xd6: '&#214;', # Ö
                     0xdc: '&#220;', # Ü
                     0xe4: '&#228;', # ä
                     0xf6: '&#246;', # ö
                     0xfc: '&#252;'} # ü
            # source: http://www.idautomation.com/product-support/ascii-chart-char-set.html
            nonasciire = re.compile(u'([\x00-\x7f]+)|([^\x00-\x7f])', re.UNICODE).sub
            email_soup = str(nonasciire(lambda x: x.group(1) or xlate.setdefault(ord(x.group(2)), '&#9647;'), soup ))
            email_text = "<!DOCTYPE html><html><body><em>" + email_soup + \
                         "</em><br><p>(Text ist direkt von der AEG Website - Klicke den oberen Link um direkt zum " \
                         "m&ouml;glicherweise neuen Stundenplan [.pdf] zu kommen)</p><br><p>Fallback link: " \
                         "<a href=\"" + URL_OF_WEBSITE + "\">" + URL_OF_WEBSITE + "</a></p></body></html>"

            DIR_OF_GMAIL_API_FILES = os.path.join(DIR_OF_SCRIPT, os.path.join("SendGmailSimplified", "gmail_api_files"))
            PATH_OF_CLIENT_DATA = os.path.join(DIR_OF_GMAIL_API_FILES, "client_data.json")
            PATH_OF_CLIENT_SECRET = os.path.join(DIR_OF_GMAIL_API_FILES, "client_secret.json")
            GmailServer = SimplifiedGmailApi(PATH_OF_CLIENT_DATA, PATH_OF_CLIENT_SECRET, DIR_OF_GMAIL_API_FILES)

            for recipient in RECIPIENTS:
                GmailServer.send_html(recipient, "Neuer Stundenplan?", email_text)

        # And save the new information
        with open(PATH_OF_DATA_FILE, 'w') as outfile:
            json.dump(soup, outfile)

        print("Change detected. New content: " + soup)
        logging.info("Change detected. New content: " + soup)
    else:
        print("No change detected.")
        logging.info("No change detected.")
