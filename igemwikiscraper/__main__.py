#!/usr/bin/python3

import argparse
import csv
import json
import string

from scraper import WikiScraper, prettify_subpages


# Create arguments for commandline tool
parser = argparse.ArgumentParser(description=
    """Virginia iGEM 2018's iGEM Wiki Webscraper. Pulls HTML from relevant
    iGEM pages parses through them to extract project descriptions. Used to
    discover other teams for potential collaboration. Not all parameters can 
    be set via flags, see config.json for further configuration options.""")
parser.add_argument('data', nargs='*', help='Path to .csv file containing team name information. Retrieve from https://igem.org/Team_List. Alternatively specify a single team name, which can be found on the wiki as http://<year>.igem.org/Team:<team-name>')
parser.add_argument('--config', '-c', help='Configuration file to use. Pass in arguments with this file.', default='config.json')
parser.add_argument('--subpages', '-s', nargs='*', help='Subpages. In addition to the base URL, these subpages will be scraped. Examples would be /Description or /Parts')
parser.add_argument('--output', '-o', help='CSV file to output data to.')
parser.add_argument('--verbose', '-v', action='count', help='Verbosity level. -v prints summary of each wiki scrape. -vv prints the contents of each wiki scrape. Omit to recieve only progress notifications.')
parser.add_argument('--start', type=int, help='First team to pull from datafile. 0-indexed.')
parser.add_argument('--end', type=int, help='Last team to pull from datafile.')
parser.add_argument('--gracetime', '-g', type=float, help='Time to wait between scrapes.')


def main():
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
            elif name == 'start':
                config['data']['start'] = arg
            elif name == 'end':
                config['data']['end'] = arg
            elif name == 'gracetime':
                config['scraper']['gracetime'] = arg
    
    # Create WikiScraper with loaded config file
    scraper = WikiScraper(config)


    # Open CSV file that we'll write our information to
    outfile = csv.writer(open(config['output']['outputfile'], 'w+'), 
                         delimiter=config['output']['filedelimiter'],  
                         quotechar=config['output']['filequotechar'])

    for datafile in config['data']['datafile']:
        # Open CSV file containing teams
        teams = csv.reader(open(datafile, newline=''),
                           delimiter=config['data']['filedelimiter'])
        # Teamcount is used to determine how close we are to done and when we
        # should terminate.
        teamcount = 0
        totalteams = config['data']['end'] - config['data']['start']
        for team in teams:
            if teamcount == 0:
                outfile.writerow(team + ['Scrape Successful?'] + prettify_subpages(config['data']['subpages']))
                teamcount = teamcount + 1
                continue
            elif teamcount < config['data']['start']:
                teamcount = teamcount + 1
                continue
            elif teamcount > config['data']['end']:
                break
            elif teamcount == config['data']['start'] + totalteams / 4:
                print('25% of wikis scraped')
            elif teamcount == config['data']['start'] + totalteams / 2:
                print('50% of wikis scraped')
            elif teamcount == config['data']['start'] + totalteams * 3 / 4:
                print('75% of wikis scraped')
            elif teamcount > config['data']['start'] + totalteams:
                print('100% of wikis scraped')
                
            teamdata = scraper.scrape(team)
            # Flatten team data using list comprehensions
            concatenateddata = []
            for data in teamdata:
                concatenateddata.append('\n'.join(data).replace("\n",r"\n").replace("\t",r"\t"))

            outfile.writerow(team + concatenateddata)

            if config['output']['verbose'] > 1:
                print('======================================================================')

            teamcount = teamcount + 1

if __name__ == "__main__":
    main()
