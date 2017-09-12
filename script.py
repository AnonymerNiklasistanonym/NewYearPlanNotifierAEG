# -*- coding: utf-8 -*-

"""
Script that scrapes the website with the year plans of the AlbertEeinsteinGymnasium.
If desired it sends emails to entered recipients (line 39+) over the SimplifiedGmailApi.
"""

# My imports (the crawler)
import json
import logging
import os
import re

import httplib2
import requests
from bs4 import BeautifulSoup


# Gmail Imports (not important for the actual crawler)
from SendGmailSimplified.SendGmailSimplified import SimplifiedGmailApi

# Paths for important directories and files - from home directory
HOME_DIR = os.path.expanduser('~')

# change this to the directory your script is: !!!!!!!!!!!!!!!!!
DIR_OF_SCRIPT = os.path.join(HOME_DIR,
                             os.path.join("Documents", "NewYearPlanNotifierAEG"))
# Documents/GitHubBeta

PATH_FOR_LOG = os.path.join(DIR_OF_SCRIPT, "script.log")
PATH_OF_DATA_FILE = os.path.join(DIR_OF_SCRIPT, 'data.json')
PATH_OF_HTML_FILE = os.path.join(DIR_OF_SCRIPT, 'data.html')

logging.basicConfig(filename=PATH_FOR_LOG, level=logging.DEBUG)

# Setup the Gmail API - set USE_GMAIL False if you want to use the Simplified Gmail API
USE_GMAIL = False

if USE_GMAIL:
    RECIPIENTS = ["yourEmailAdress@sonstwas.com", "onemore@gmail.com"]

URL_OF_WEBSITE = "http://www.aeg-boeblingen.de/index.php/aktuelles/stundenplan"

# get website content by using a Cookie
try:
    logging.info("Try getting the website " + URL_OF_WEBSITE + ":")
    HTTP = httplib2.Http()
    HEADERS = {
        'Cookie': "6024a7383aa153ec184c3ea3382596a7=fli24m6oth1a2p43d8a7d64vs7"}
    RESPONSE, CONTENT = HTTP.request(URL_OF_WEBSITE, 'GET', headers=HEADERS)
except requests.HTTPError as err:
    logging.warning(err)
except requests.ConnectionError as err:
    logging.warning(err)
else:
    logging.info("Process was successful.")

    # Now crawl the information from the website:
    SOUP_HTML_DATA = BeautifulSoup(CONTENT, 'html.parser')
    # get all div's with the class custom
    SOUP_HTML_DATA = SOUP_HTML_DATA.find_all('div', {'class': 'custom'})[1]
    # took the second one and get the p tag from it as a String
    SOUP_HTML_DATA = str(SOUP_HTML_DATA)
    # replace all extra lines (\n) with nothing
    SOUP_HTML_DATA = SOUP_HTML_DATA.replace("\n", "")
    # repair all the links so that they are usable
    SOUP_HTML_DATA = SOUP_HTML_DATA.replace(
        "href=\"/", "href=\"http://www.aeg-boeblingen.de/")

    # Load the old file information if it exists
    if os.path.isfile(PATH_OF_DATA_FILE):
        with open(PATH_OF_DATA_FILE) as data_file:
            JSON_DATA_SAVED_FILE = json.load(data_file)

        # Convert the data into JSON format if old data exists
        JSON_DATA_WEBSITE = json.loads(json.dumps(SOUP_HTML_DATA))
    else:
        JSON_DATA_SAVED_FILE, JSON_DATA_WEBSITE = None, None

    # Check if the old file is different from the current information
    if JSON_DATA_SAVED_FILE is None or JSON_DATA_WEBSITE != JSON_DATA_SAVED_FILE:

        # If yes send a HTML email to all recipients
        if USE_GMAIL:

            # algorithm encoding source:
            # http://code.activestate.com/recipes/251871-latin1-to-ascii-the-unicode-hammer/
            XLATE_TABLE = {0xdf: '&#223;',  # ß
                           0xc4: '&#196;',  # Ä
                           0xd6: '&#214;',  # Ö
                           0xdc: '&#220;',  # Ü
                           0xe4: '&#228;',  # ä
                           0xf6: '&#246;',  # ö
                           0xfc: '&#252;'}  # ü
            # source: http://www.idautomation.com/product-support/ascii-chart-char-set.html
            NON_ASCII_RE = re.compile(
                u'([\x00-\x7f]+)|([^\x00-\x7f])', re.UNICODE).sub
            EMAIL_NEW_DATA = str(NON_ASCII_RE(lambda x: x.group(1) or
                                              XLATE_TABLE.setdefault(ord(x.group(2)),
                                                                     '&#9647;'), SOUP_HTML_DATA))
            EMAIL_TEXT = ("<!DOCTYPE html><html><body><em>" + EMAIL_NEW_DATA + "</em><br><p>" +
                          "(Text ist direkt von der AEG Website - Klicke den oberen Link um " +
                          "direkt zum m&ouml;glicherweise neuen Stundenplan [.pdf] zu kommen)" +
                          "</p><br><p>Fallback link:<a href=\"" + URL_OF_WEBSITE + "\">" +
                          URL_OF_WEBSITE + "</a></p></body></html>")

            DIR_OF_GMAIL_API_FILES = os.path.join(DIR_OF_SCRIPT,
                                                  os.path.join("SendGmailSimplified",
                                                               "gmail_api_files"))
            PATH_OF_CLIENT_DATA = os.path.join(
                DIR_OF_GMAIL_API_FILES, "client_data.json")
            PATH_OF_CLIENT_SECRET = os.path.join(
                DIR_OF_GMAIL_API_FILES, "client_secret.json")
            GMAIL_SERVER = SimplifiedGmailApi(PATH_OF_CLIENT_DATA,
                                              PATH_OF_CLIENT_SECRET,
                                              DIR_OF_GMAIL_API_FILES)

            for recipient in RECIPIENTS:
                GMAIL_SERVER.send_html(
                    recipient, "Neuer Stundenplan?", EMAIL_TEXT)

        # And save the new information
        with open(PATH_OF_DATA_FILE, 'w') as outfile:
            json.dump(SOUP_HTML_DATA, outfile)

        print("Change detected. New content: " + SOUP_HTML_DATA)
        logging.info("Change detected. New content: " + SOUP_HTML_DATA)
    else:
        print("No change detected.")
        logging.info("No change detected.")
