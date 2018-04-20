This program is designed to collect data about cat breeds and about local adoptable cats, store this data in a database, and present this data through charts and graphs. 

cats.py scrapes and crawls https://www.catbreedslist.com for information about different cat breeds. It collects the Name, Size, Life span, and Colors, as well as the
breed's level of Affection, Energy, Health Issues, Intelligence, and Shedding. The function get_one_breed takes a url for the detail page of a breed, scrapes the relevant information,
and returns it in the form of a dictionary. get_all_breeds crawls through each letter page of catbreedslist.com and collects the url for the detail page of each breed, then calls get_one_breed
 on each url, and returns a list of trait dictionaries. 

getpets.py makes requests to the Petfinder API to fetch data about adoptable cats in each breed. A class called Pet is defined that stores information about each cat.  The function 
get_breeds_list requests a list of breed names from Petfinder and filters out any breeds not listed on catbreedslist.com. Then, the function get_pets requests data abut 5 pets in each of these 
breeds and returns a list of Pet objects.
To run this file, the user needs their own API key and secret from Petfinder. The user must input these credentials into a file named secrets.py. The file named secrets_example.py 
provides the format. Documentation for this API may be found here: https://www.petfinder.com/developers/api-docs.

create_cat_db.py pulls the data collected by cats.py and getpets.py and writes the data into a database named "cats.db." Running this program on its own will refresh the database 
completely. init_db creates the database and the tables. insert_breeds populates the breeds table with the information in the trait dictionaries gathered by cats.py, with the 
exception of the colors. insert_colors iterates through the list of trait dictionaries, cleans up each list (e.x. removing "all colors"), and compiles a list of all unique colors. It uses this list to 
populate the 'colors' table, assigning a unique id to each color. insert_breedcolors_for_one takes only one trait dictionary as input, and is used to populate the BreedColors table. 
This table is used to model the many-to-many relationships between breeds and the colors that breed comes in. insert_breedcolors_for_one iterates through its color list, extracts the ids
for the bread and the color, and inserts these values as a new row in the BreedColors table. The function insert_pets inserts the pet data gathered by getpets.py,
calling on the instance variables of each Pet instance to create the row, and assigning the correct breed id to each pet.

Finally, interactive_prompt.py prompts the user for commands, which will fetch data from cats.db and provide visualization options. 
Four visualization options are available to the user: table, scatterplot, pie charts, and bar graphs. When the user passes multi-word input for a parameter, such as a breed name, 
underscores should be used instead of spaces.  Thus "breed=american_wirehair" must be used instead of "breed=american wirehair"
For bar charts, the user can choose to view the levels of one breed or compare two breeds. the bar command takes either one or three parameters:
	bar breed=exotic_shorthair
	bar compare breed1=exotic_shorthair breed2=ragdoll

Pie chars will display either the percent of breeds that come in each color (if the second parameter is 'color'), or show the percentage of nearby pets in each breed (if the second 
parameter is 'pets'). The 'color' command takes another optional parameter, 'size,' in which the user can choose to view only colors for cats of that size group:
	pie color size=large
The 'pets' command can also be specified by size as above, or the user can choose to specify by state abbreviation, or by a certain color:
	pie pets location=mi
	pie pets size=small
	pie pets color=tabby

Scatter plots allow the user to compare all breeds on two different characteristics. The user chooses which trait will be represented on the x axis and which on the y axis. Again, the 
user may specify by size or color. 
	scatter x=HealthIssues y=AffectionLevel 
	scatter x=Popularity y=Intelligence size=large

Tables are the simplest view, displaying data about each breed depending on parameters set by the user. The user may specify breed, color, or size. The user may also choose to 
display one of the trait levels: AffectionLevel, HealthIssues, Shedding, EnergyLevel, or Intelligence. The default trait shown is AffectionLevel.
	table breed=toyger trait=Intelligence
	table color=tabby trait=EnergyLevel
	table size=large

