import unittest
import sqlite3
import getpets as gp
import interactive_prompt as ip
import cats
import create_cat_db
import secrets
import json

DBNAME = 'cats.db'
CACHE_FNAME = 'catcache.json'


class TestDatabase(unittest.TestCase):

    def test_breed_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Breeds'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('toyger',), result_list)
        self.assertEqual(len(result_list), 64)

        sql = '''
            SELECT Name, Popularity, [Size], AffectionLevel FROM Breeds
            WHERE AffectionLevel <  5
            ORDER BY Popularity
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 3)
        self.assertEqual(result_list[0][0], 'aegean')

        conn.close()

    def test_color_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Name
            FROM Colors
            WHERE Name LIKE '%tabby'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('black silver spotted tabby',), result_list)
        self.assertEqual(len(result_list), 10)

        sql = '''
            SELECT COUNT(*)
            FROM Colors
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertEqual(count, 63)

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT B.Name, C.Name
            FROM BreedColors as BC
                JOIN Breeds as B
                ON B.Id=BC.BreedId
                JOIN Colors as C
                ON C.Id=BC.ColorId
            WHERE C.Name LIKE "lilac%"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('malayan','lilac point'), result_list)
        conn.close()

class TestBarSearch(unittest.TestCase):

    def test_bar_search(self):
        results = ip.process_command('bar breed=exotic_shorthair')
        self.assertEqual(results[0][1], 'exotic shorthair')

        results = ip.process_command('bar compare breed1=ragdoll breed2=toyger')
        self.assertEqual(results[0][1], 'ragdoll')
        self.assertEqual(results[1][1], 'toyger')


class TestPieSearch(unittest.TestCase):

    def test_pie_search(self):
        results = ip.process_command('pie color size=large')
        self.assertEqual(results[1], ('black',3))

class TestTableSearch(unittest.TestCase):

    def test_table_search(self):
        results = ip.process_command('table breed=birman')
        self.assertEqual(results[0],('birman', 'large', 15, '14-15 years', 5))

        results = ip.process_command('table color=chocolate trait=Shedding top=20')
        self.assertEqual(results[1], ('american shorthair', 'large', 6, '15-17 years', 5))

        results = ip.process_command('table size=small trait=HealthIssues bottom=10')
        self.assertEqual(results[2][0], 'munchkin')


class TestScatterSearch(unittest.TestCase):

    def test_scatter_search(self):
        results = ip.process_command('scatter x=Intelligence y=EnergyLevel')
        self.assertEqual(results[2], ('american bobtail', 5, 3))

        results = ip.process_command('scatter x=Popularity y=HealthIssues size=large')
        self.assertEqual(results[6], ('birman', 15, 3))

class TestCache(unittest.TestCase):
    def test_cache(self):
        url='http://api.petfinder.com/pet.find'
        params = {'format':'json', 'count':5, 'animal' :'cat','breed':'Chinchilla', 'key':secrets.api_key, 'location':'MI'}
        response = gp.get_pets('Chinchilla')
        with open(CACHE_FNAME, 'r') as cache_file:
            cache_contents = cache_file.read()
            CACHE_DICTION = json.loads(cache_contents)
        self.assertIn(gp.get_ui(url,params),CACHE_DICTION)


unittest.main()
