#!/usr/bin/python3

from scraper import simple_get
from bs4 import BeautifulSoup
import csv
import re


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
