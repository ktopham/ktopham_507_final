import sqlite3
import json
import cats

DBNAME = 'cats.db'



def init_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
    except:
        print("whoopsydaisy")

    statement2 = '''
        DROP TABLE IF EXISTS 'Breeds';
    '''
    cur.execute(statement2)
    conn.commit()
    make_table1 = '''
        CREATE TABLE IF NOT EXISTS 'Breeds' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'Popularity' INTEGER,
            'Size' TEXT,
            'LifeSpan' TEXT,
            'AffectionLevel' INTEGER,
            'EnergyLevel' INTEGER,
            'HealthIssues' INTEGER,
            'Intelligence' INTEGER,
            'Shedding' INTEGER
        );
    '''
    cur.execute(make_table1)
    conn.commit()

    statement4 = '''
        DROP TABLE IF EXISTS 'Colors';
    '''
    cur.execute(statement4)
    conn.commit()
    make_table2 = '''
        CREATE TABLE IF NOT EXISTS 'Colors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL
        );
    '''
    cur.execute(make_table2)
    conn.commit()
    statement5 = '''
        DROP TABLE IF EXISTS 'BreedColors';
    '''
    cur.execute(statement5)
    conn.commit()
    make_table3 = '''
        CREATE TABLE IF NOT EXISTS 'BreedColors' (
            'ColorId' INTEGER,
            'BreedId' INTEGER
        );
    '''
    cur.execute(make_table3)
    conn.commit()
    statement4 = '''
        DROP TABLE IF EXISTS 'Pets';
    '''
    cur.execute(statement4)
    conn.commit()
    make_table4 = '''
        CREATE TABLE IF NOT EXISTS 'Pets' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Size' TEXT,
            'Sex' TEXT,
            'Location' TEXT,
            'BreedId' INTEGER
        );
    '''
    cur.execute(make_table4)
    conn.commit()
    conn.close()
#creates a database with two tables: Breeds, Colors, BreedColors
#takes nothing, returns nothing

def insert_breeds(dict_list):
    for trait_dict in dict_list:
        insert = (trait_dict['Name'], trait_dict['Popularity'], trait_dict['Size'], trait_dict['Life span'], trait_dict['Affection Level'],trait_dict['Energy Level'],trait_dict['Health Issues'],trait_dict['Intelligence'],trait_dict['Shedding'])
        statement = 'INSERT INTO "Breeds" '
        statement += 'VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        with sqlite3.connect(DBNAME) as conn:
            cur = conn.cursor()
            cur.execute(statement, insert)
            conn.commit()


#params: list of dictionaries about cat breeds
#turns tup into
# inserts each tup into its appropriate column in the Breed table

def insert_colors(dict_list):
    colors = []
    for trait_dict in dict_list:
        # tup_list.append((trait_dict['Name'], trait_dict['Popularity'], trait_dict['Size'], trait_dict['Life span'], trait_dict['Affection Level'],trait_dict['Energy Level'],trait_dict['Health Issues'],trait_dict['Intelligence'],trait_dict['Shedding']))
        indiv_colors = []
        for color in trait_dict['Colors']:
            breed_color = color.lower().strip("'")
            if "..." in breed_color:
                continue
            elif "exception" in breed_color:
                continue
            elif "all" in breed_color:
                trait_dict['Colors'][trait_dict['Colors'].index(color)] = "variety"
            if breed_color not in colors:
                colors.append(breed_color)
            indiv_colors.append(breed_color)
        trait_dict['Colors'] = indiv_colors

    for color in colors:
        statement = 'INSERT INTO "Colors" '
        statement += 'VALUES (NULL, "' + color + '" )'
        insert = color
        with sqlite3.connect(DBNAME) as conn:
            cur = conn.cursor()
            cur.execute(statement)
            conn.commit()

# params: the list of breed characteristic dicts
#builds the colors list
# inserts colors into the db, just name and id


def insert_breedcolors_for_one(trait_dict):
    get_breed_id = '''SELECT Id FROM "Breeds" WHERE Name = "''' + trait_dict["Name"] + '''"'''
    with sqlite3.connect(DBNAME) as conn:
        cur = conn.cursor()
        cur.execute(get_breed_id)
        for row in cur:
            breed_id = row[0]
    for color in trait_dict['Colors']:
        get_color_id = '''SELECT Id FROM "Colors" WHERE Name = "''' + color + '''" '''
        with sqlite3.connect(DBNAME) as conn:
            cur = conn.cursor()
            cur.execute(get_color_id)
            for row in cur:
                color_id = row[0]
        statement = '''INSERT INTO "BreedColors" '''
        statement += '''VALUES (?, ?) '''
        insert = (breed_id, color_id)
        with sqlite3.connect(DBNAME) as conn:
            cur = conn.cursor()
            cur.execute(statement, insert)
            conn.commit()
# params: a trait dictionary
# iterates through trait_dict['Colors']
# inserts tuple: (BreedId, ColorId)
#'select BreedId where name like '+ trait_dict['Name']
#for color in trait_dict['colors']:
    #'select colorid where color like ' + Color
    #tup = (BreedId, ColorId)
    #'insert into BreedColors' tup

def insert_pets(pet_list):
    with sqlite3.connect(DBNAME) as conn:
        cur = conn.cursor()
        for pet in pet_list:
            get_id = '''SELECT Id FROM Breeds WHERE Name LIKE "%'''
            get_id += pet.breed + '''%" '''
            cur.execute(get_id)
            for row in cur:
                breed_id = row[0]
                insert = (pet.name, pet.size, pet.sex, pet.location, breed_id)
                statement = 'INSERT INTO "Pets" '
                statement += 'VALUES (NULL, ?, ?, ?, ?, ?)'
                cur.execute(statement, insert)
                conn.commit()


def create_and_pop_db():
    init_db()
    breed_dicts = cats.get_all_breeds()
    insert_breeds(breed_dicts)
    insert_colors(breed_dicts)
    for dict in breed_dicts:
        insert_breedcolors_for_one(dict)
    breeds_list = getpets.get_breeds_list()
    for breed in breeds_list:
        pet_list = getpets.get_pets(breed)
        insert_pets(pet_list)

if __name__ == '__main__':
    create_and_pop_db()
