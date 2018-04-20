import secrets
import requests
import json

CACHE_FNAME = 'catcache.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

class Pet():
    def __init__(self, breed, dictionary):
        try:
            self.name = dictionary['name']['$t']
        except:
            self.name = 'Socks'
        self.breed = breed
        self.sex = dictionary['sex']['$t']
        self.city = dictionary['contact']['city']['$t']
        self.state = dictionary['contact']['state']['$t']
        self.location = self.city + ', ' + self.state
        if "S" in dictionary['size']['$t']:
            self.size = 'small'
        elif "L" in dictionary['size']['$t']:
            self.size = 'large'
        else:
            self.size = "medium"

    def __str__(self):
        return "My name is {}! I'm a {} {} in {}.".format(self.name, self.size, self.breed, self.location)

def get_ui(url, params):
    alphabetized_keys = sorted(params.keys())
    res = ["{}+{}".format(k, params[k]) for k in alphabetized_keys]
    return url + "_".join(res)

def get_pets(breedname):
    url='http://api.petfinder.com/pet.find'
    params = {'format':'json', 'count':5, 'animal' :'cat','breed':breedname, 'key':secrets.api_key, 'location':'MI'}
    ui = get_ui(url, params)
    if ui in CACHE_DICTION:
        resp_dict = CACHE_DICTION[ui]
    else:
        resp = requests.get(url, params)
        resp_dict = json.loads(resp.text)
        CACHE_DICTION[ui] = resp_dict
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
    pet_list=[]
    if breedname == 'Extra-Toes Cat / Hemingway Polydactyl':
        breedname = 'american polydactyl'
    if 'Sphynx' in breedname:
        breedname = 'sphynx'
    if 'Oriental' in breedname:
        breedname = 'oriental'
    if 'pet' in resp_dict['petfinder']['pets'].keys():
        if type(resp_dict['petfinder']['pets']['pet']) == type(['a','b']):
            for pet in resp_dict['petfinder']['pets']['pet']:
                pet_list.append(Pet(breedname.lower(), pet))
        elif type(resp_dict['petfinder']['pets']['pet']) == type({'a':'b'}):
            pet_list.append(Pet(breedname, resp_dict['petfinder']['pets']['pet']))
    return pet_list


def get_breeds_list():
    url = 'http://api.petfinder.com/breed.list'
    params = {'format':'json', 'animal':'cat', 'key':secrets.api_key}
    ui = get_ui(url, params)
    if ui in CACHE_DICTION:
        resp_dict = CACHE_DICTION[ui]
    else:
        resp = requests.get(url, params)
        resp_dict = json.loads(resp.text)
        CACHE_DICTION[ui] = resp_dict
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
    ret_list = [d['$t'] for d in resp_dict['petfinder']['breeds']['breed']]
    forbidden = ['Applehead Siamese', 'Bengal', 'Calico', 'Canadian Hairless', 'Chinchilla', 'Devon Rex', 'Dilute Calico', 'Dilute Tortoiseshell','Siberian','Korat', 'Domestic Short Hair', 'Domestic Long Hair', 'Domestic Medium Hair', 'Oriental Long Hair', 'Oriental Tabby','Silver','Tiger', 'Torbie', 'Tabby', 'Tortoiseshell', 'Tuxedo']
    breeds_list = []
    for b in ret_list:
        if b not in forbidden:
            breeds_list.append(b)
    return breeds_list
