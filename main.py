#!/usr/bin/python3

import argparse
from bs4 import BeautifulSoup
import csv
import re
import json

from scraper import simple_get


parser = argparse.ArgumentParser(description=
    """Virginia iGEM 2018's iGEM Wiki Webscraper. Pulls HTML from relevant
    iGEM pages parses through them to extract project descriptions. Used to
    discover other teams for potential collaboration. Not all parameters can be set via flags, see config.json for further configuration options.""")
parser.add_argument('data', help='Path to .csv file containing team name information. Retrieve from https://igem.org/Team_List. Alternatively specify a single team name, which can be found on the wiki as http://<year>.igem.org/Team:<team-name>')
parser.add_argument('--config', '-c', help='Configuration file to use. Pass in arguments with this file.', default='config.json')
parser.add_argument('--year', '-y', help='Team year. Needed to generate URLs for pulling information.')
parser.add_argument('--subpages', '-s', help='Subpages. In addition to the base URL, these subpages will be scraped. Examples would be /Description or /Parts')
parser.add_argument('--output', '-o', help='CSV file to output data to.')
parser.add_argument('--verbose', '-v', action='count')
parser.add_argument('--start', type=int, help='First team to pull from datafile. 0-indexed.')
parser.add_argument('--end', type=int, help='Last team to pull from datafile.')


def assemble_urls(year, name, subpages=['']):
    urls = []
    url_base = 'http://' + year + '.igem.org/Team:' + name
    for s in subpages:
        urls.append(url_base + s)
    return urls

def prettify_subpages(subpages):
    output = subpages.copy()
    for index, page in enumerate(subpages):
        if page == '':
            output[index] = 'Homepage'
    return output

if __name__ == '__main__':
    args = parser.parse_args() # Pull down cmdline arguments

    config = json.load(open(args.config, 'r')) # Load config file

    # Overwrite config file options with command line arguments if they are passed
    # TODO: Make this more elegant than just a bunch of if statements
    for name, arg in args.__dict__.items():
        if arg != None:
            if name == 'output':
                config['output']['outputfile'] = arg
            elif name == 'data':
                config['data']['datafile'] = arg
            elif name == 'subpages':
                config['data']['subpages'] = arg
            elif name == 'verbose':
                config['output']['verbose'] = arg
            elif name == 'year':
                config['data']['year'] = arg
            elif name == 'start':
                config['data']['start'] = arg
            elif name == 'end':
                config['data']['end'] = arg
    
    # Filters out paragraph tags that are probably not descriptions.
    def strain(paragraph):
        return (paragraph.count(' ') > config['strainer']['space_count']  # More than x spaces
            and paragraph.count('.') > config['strainer']['period_count'] # At least y periods
            and not re.search(config['strainer']['regex'], paragraph)) # Does not contain common JavaScript syntax

    # Open CSV file containing teams
    teams = csv.reader(open(config['data']['datafile'], newline=''), delimiter=config['data']['filedelimiter'])

    # Open CSV file that we'll write our information to
    outfile = csv.writer(open(config['output']['outputfile'], 'w+'), delimiter=config['output']['filedelimiter'], quotechar=config['output']['filequotechar'])

    teamcount = 0
    totalteams = config['data']['end'] - config['data']['start']
    for team in teams:
        if teamcount == 0:
            outfile.writerow(team + prettify_subpages(config['data']['subpages']))
            teamcount = teamcount + 1
            continue
        elif teamcount > totalteams:
            break
        elif teamcount == totalteams / 4:
            print('25% of wikis scraped')
        elif teamcount == totalteams / 2:
            print('50% of wikis scraped')
        elif teamcount == totalteams * 3 / 4:
            print('75% of wikis scraped')
        elif teamcount == totalteams:
            print('100% of wikis scraped')
            

        year = team[8]
        name = team[1]
        valid = team[7] == 'Accepted'

        writeline = ""

        writeline = team.copy()

        if valid:
            urls = assemble_urls(year, name, config['data']['subpages'])

            # Extract HTML from URLs, spit out parsable BeautifulSoup objects
            for index, url in enumerate(urls):
                raw_html = simple_get(url)
                html = BeautifulSoup(raw_html, 'html.parser')
            
                if config['output']['print']:
                    print(name + ' ' + year + ' ' +  prettify_subpages(config['data']['subpages'])[index] + '\n')

                output = ""

                for tag in html.select(config['data']['htmlselector']):
                    if strain(tag.text):
                        if config['output']['print']:
                            print(tag.text + '\n')
                        output += tag.text + '\n'
                print(len(html.select(config['data']['htmlselector'])))

                writeline.append(output)

            
        if config['output']['print']:
            print('--------------------------------------------------')
        outfile.writerow(writeline)
        teamcount = teamcount + 1
