pip install igemwikiscraper
mkdir igem-scrapes
cd igem-scrapes
curl https://raw.githubusercontent.com/Virginia-iGEM/igem-wikiscraper/master/igemwikiscraper/config.json -o config.json
mkdir data
mkdir output
cd data
curl https://raw.githubusercontent.com/Virginia-iGEM/igem-wikiscraper/master/data/2018__team_list__2018-07-02.csv -o 2018__team_list__2018-07-02.csv
cd ..
echo "wikiscraper-gui" > wikiscraper-gui.sh
