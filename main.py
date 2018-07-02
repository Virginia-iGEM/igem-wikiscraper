#!/usr/bin/python3

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv

import re

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def is_description(paragraph):
    return (paragraph.count(' ') > 10  # More than 10 spaces
        and paragraph.count('.') > 2 # At least three periods
        and not re.search('(function\(\) \{|$\()', paragraph)) # Does not contain common JavaScript syntax

if __name__ == '__main__':
    team_year = '2018'
    team_name = 'SHSBNU_China'
    url_base = 'http://' + team_year + '.igem.org/Team:' + team_name
    url_project = url_base + '/Description'
    urls = [url_base, url_project]
    htmls = []
    for url in urls:
        raw_html = simple_get(url)
        htmls.append(BeautifulSoup(raw_html, 'html.parser'))
    
    #print(raw_html)
    print('Potential Description Paragraphs for ' + team_name + ' ' + team_year + '\n')
    for html in htmls:
        for p in html.select('p'):
            if is_description(p.text):
                print(p.text + '\n')
