#!/usr/bin/python3

import argparse
import csv
import json
import string
import os
import platform
import sys

from gooey import Gooey, GooeyParser

from igemwikiscraper.scraper import WikiScraper, prettify_subpages

def core(gui=False):
    # Create arguments for commandline/gui tool
    parser = GooeyParser(description=
        """Virginia iGEM 2018's iGEM Wiki Webscraper.""",
        epilog="""
        Pulls HTML from relevant iGEM pages parses through them to extract 
        project descriptions. Not all parameters can be set via flags, see 
        config.json for further configuration options.""")

    main_args = parser.add_argument_group("Main", "Required to scrape data.")
    option_args = parser.add_argument_group("Options", "Override settings in config.json. Use of config.json is reccommended over setting these.")

    main_args.add_argument('data', nargs='*', help='Path to .csv file containing team name information. Retrieve from https://igem.org/Team_List. Alternatively specify a single team name, which can be found on the wiki as http://<year>.igem.org/Team:<team-name>', widget='FileChooser')
    main_args.add_argument('--config', '-c', help='Configuration file to use. Pass in arguments with this file.', default='config.json', widget='FileChooser')

    option_args.add_argument('--output', '-o', help='CSV file to output data to.', widget='FileSaver')
    option_args.add_argument('--subpages', '-s', nargs='*', help='Subpages to scrape. Such as /Description or /Parts')
    option_args.add_argument('--verbose', '-v', action='count', help='-v print summaries. -vv print full contents. Omit to recieve only progress notifications.')
    option_args.add_argument('--start', type=int, help='First team to pull from datafile. 0-indexed.')
    option_args.add_argument('--end', type=int, help='Last team to pull from datafile.')
    option_args.add_argument('--gracetime', '-g', type=float, help='Time to wait between scrapes.')

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
    scraper = WikiScraper(config, gui=gui)

    # Open CSV file that we'll write our information to
    outfile = csv.writer(open(config['output']['outputfile'], 'w+', encoding='utf-8'), 
                         delimiter=config['output']['filedelimiter'],  
                         quotechar=config['output']['filequotechar'])

    for datafile in config['data']['datafile']:
        # Open CSV file containing teams
        teamfile = open(datafile, newline='')
        teams = csv.reader(teamfile,
                           delimiter=config['data']['filedelimiter'])

        if ('start' not in config['data'] or config['data']['start'] == -1):
            config['data']['start'] = 0
        if ('end' not in config['data'] or config['data']['end'] == -1):
            config['data']['end'] = sum(1 for row in teams)
            teamfile.seek(0) # reset iterator to beginning of file
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
                print('25% of wikis scraped', flush=gui)
            elif teamcount == config['data']['start'] + totalteams / 2:
                print('50% of wikis scraped', flush=gui)
            elif teamcount == config['data']['start'] + totalteams * 3 / 4:
                print('75% of wikis scraped', flush=gui)
            elif teamcount > config['data']['start'] + totalteams:
                print('100% of wikis scraped', flush=gui)
                
            teamdata = scraper.scrape(team)
            # Flatten team data using list comprehensions
            concatenateddata = []
            for data in teamdata:
                concatenateddata.append(data)

            outfile.writerow(team + concatenateddata)

            teamcount = teamcount + 1

if platform.system() == 'Windows':
    target = 'wikiscraper-gui.exe'
else:
    target = 'wikiscraper-gui'

@Gooey(
    program_name='iGEM Wikiscraper',
    advanced=True,
    tabbed_groups=True,
    image_dir=os.path.dirname(__file__),
    target=target
)
def gui():
    core(gui=True)

def main():
    core(gui=False)

if __name__ == "__main__":
    main()
