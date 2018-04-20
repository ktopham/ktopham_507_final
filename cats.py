from string import ascii_uppercase
from bs4 import BeautifulSoup
import getpets
import requests
import sqlite3
import json



CACHE_FNAME = 'catcache.json'
DBNAME = 'cats.db'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def get_all_breeds():
    baseurl = 'http://www.catbreedslist.com/Tags-'
    urls = []
    for c in ascii_uppercase:
        url = baseurl + c
        if url in CACHE_DICTION:
            resp = CACHE_DICTION[url]
        else:
            print("making new request...")
            resp = requests.get(url = url).text
            CACHE_DICTION[url] = resp
            dumped_json_cache = json.dumps(CACHE_DICTION)
            fw = open(CACHE_FNAME,"w")
            fw.write(dumped_json_cache)
            fw.close()
        page_soup = BeautifulSoup(resp, 'html.parser')
        results = page_soup.find_all('div', class_ ='list')

        for div in results:
            for child in div.children:
                a = child.find('a')
                try:
                    urls.append(a['href'])
                except:
                    href = False
    dict_list = []

    for url in urls:
        trait_dict = get_one_breed(url)
        dict_list.append(trait_dict)
    return dict_list
#scrape each tag page for the href referenced in breed name
# writes data to cache, url is identifier
#calls get_one_breed on all kitties on each page
#returns: list of dictionaries about each breed
def get_one_breed(href):
    if href in CACHE_DICTION:
        resp = CACHE_DICTION[href]
    else:
        resp = requests.get(url = href).text
        CACHE_DICTION[href] = resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
    page_soup = BeautifulSoup(resp, 'html.parser')
    table = page_soup.find_all('tr')
    traits = ['Popularity (2014)','Name','Size','Life span','Colors','Affection Level','Energy Level','Health Issues','Intelligence','Shedding']
    trait_dict = {}
    for tr in table:
        tds = tr.find_all('td')
        for td in tds:
            if td.has_attr('class'):
                if td.text in traits:
                    left = td.text
                    i = tds.index(td)
                    td2 = tds[i+1]

                    if left == 'Popularity (2014)':
                        if len(td2.text) == 2:
                            right = int(td2.text[1])
                        elif len(td2.text) == 3:
                            right = int(td2.text[1:])
                        else:
                            right = 0
                        left = 'Popularity'
                    elif 'stars' in td2.text:
                        right = int(td2.text[0])
                    elif left == "Colors":
                        right = [item.string for item in td2]
                    else:
                        right = td2.text.lower()
                        if "large" in right:
                            right = "large"
                        elif "small" in right:
                            right = "small"
                    trait_dict[left] = right
    return trait_dict
#params: url for page to scrape
#scrapes info about one breed
#store data in cache: url is identifier
#returns one dictionary about that breed
