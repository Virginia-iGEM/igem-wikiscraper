# igem-wikiscraper

A quick-and-dirty Python CLI tool for scraping iGEM wikis. Can be used to pull out any relevant HTML-based information. Note that this tool will not function on, for example, lab manuals involving PDFs, pages that dynamically load in content on user interaction or page scroll, or pages that redirect to other websites (not that this is allowed by iGEM).

## Use

This tool currently only functions with Python3. Python2 compatibility is on the backburner.

### GUI

We've built a user-friendly GUI for this tool if you prefer pressing buttons. It still requires configuration as detailed under [Configuration](#configuration) using a text editor such as Notepad or Vim.

### Command Line

1. Clone `igem-wikiscraper` somewhere out of the way, like `~/.install`.
2. Enter repository, then install with `cd igem-wikiscraper` and `./install.sh`
  - Note for Windows users: install.sh will likely not work. Instead type either `pip install -e .` or `pip3 install -e .` depending on the name of your Python3 pip tool.
3. Leave the repository. Create a new folder to store your input and output data.
4. Copy `config.json` from the cloned `igem-wikiscraper/igemwikiscraper` directory into your new folder.
5. Modify `config.json` as you see fit. Descriptions of config options are available below.
6. Run `wikiscraper [teamlist.csv]` from this new folder, where `[teamlist.csv]` is the path to a .csv list of iGEM teams. These files can be found at https://igem.org/Team_List

#### Example Command Sequence

```bash
git clone https://github.com/Virginia-iGEM/igem-wikiscraper.git
cd igem-wikiscraper
sudo ./install.sh
cd ..
mkdir new_scrape
cp igem-wikiscraper/wikiscraper/config.json -t new_scrape
cd new_scrape
mkdir data output
cd data
wget "https://igem.org/Team_List.cgi?jamboree=91&team_list_download=1"
cd ..
wikiscraper data/2018__team_list__[YOUR DATE HERE].csv
```

Output file can be found under `output/` or as configured.

## Brief Description of Tool Function

The tool retrieves raw HTML from URLs generated from a list of team names and years. This raw HTML is then passed through BeautifulSoup, a combination HTML Parser and HTML Selector built specifically for webscraping. 

Specific HTML tags are removed in preprocessing (such as script and style tags, which we don't need), then a set of tags is selected with an emulated JQuery selector (with the `htmlselector` option). This set of tags is then "strained" by their content, removing entries that are too short, do not contain sentences, and which contain any JavaScript or CSS motifs.

All of the children of selected tags are then unwrapped, discarding their attributes and keeping only their content in (what I believe is) a pre-ordered tree traversal. 

This process occurs for each page specified by `subpages`, leaving us with a list of lists of strings for each team. This 2d list is flattened to 1d by joining the sublists with newlines, before being appended to team information and written out as one row in a .csv file specified by `outputfile`. This is repeated for each team in the teamlist, building up a list of team information paired with useful scraped data.

## Configuration

Note: Some of these options can be set when using the CLI. Enter `wikiscraper -h` for a list of options which can be set through the CLI. This is convenient for options like `-vv` which you may not want to see on every scrape attempt.

- data: Options for what kind of data we take in and look for
  - subpages: Which pages on the wiki to look at. `""` denotes the index. Note that each page is lead with a forward slash; every page must be lead with a forward slash. Examples: `/Team`, `/Safety`
  - filedelimiter: What kind of csv delimiter is the team name list using? The iGEM Team List page seems to generate CSV's with comma delimiters.
  - start: Which team in the list to start with.
  - end: Which team in the list to end with
- scraper: Options for how the scraper filters and interprets data
  - htmlselector: JQuery-style selector for html elements. `#content` seems to include all hand-written team info without including any extra junk. Upon inspecting many iGEM wikis, we found all content _should_ be wrapped in `#mw-content-text`, but because there are _so many_ (about 10% of) iGEM wikis with broken HTML, mostly in the form of unpaired HTML tags, we have to be a bit generous with our selectors.
  - gracetime: Number of seconds to wait between HTML GET requests. Strongly reccommend this to be kept at 1 or above; any lower is considered impolite by web scraping standards, may break the iGEM Wiki, and may be considered a crime (a Denial of Service Attack, albeit a poor one).
  - stripwhitespace: Removes leading and trailing whitespace. Cleans up output a little.
  - collapsenewlines: Removes strings of newlines in retrieved strings
  - excisescripts: Removes any script tags when preprocessing HTML
  - excisestyles: Removes any style tags when preprocessing HTML
  - use: Enables/disables filters listed below.
  - space_count: Filters strings by the number of spaces they contain. If a string has less than this number of spaces, it will be excluded.
  - period_count: Filters string by number of periods contained. If a string has less than this number of periods, it will be excluded.
  - negative_regex: Regex with double-escaped backslashes. If a string matches this regex, it will be excluded.
- output: Options for the output file
  - outputfile: Path to the file we output our results to.
  - filedelimiter: Delimits columns in the output .csv file. Default is a vertical pipe, `|`, useful for plain HTML content.
  - filequotechar: Used to encapsulate escaped strings in .csv files. Doublequotes `"` are fairly standard.
  - verbose: Set to `0` to print progress reports only. Set to `1` to print useful information above each wiki page scraped. Set to `2` to print all content scraped.

## Todo

- Expand collapsenewlines option to also collapse strings of newlines and tabs into just one newline
- Make it so that options under `scraper.use` actually enable/disable the filter
- Replace `excisescripts` and `excisestyles` flags with an HTML selector that excises arbitrary HTML elements
- Either enable output to multiple files or ensure multiple inputs lead to a sane single output
