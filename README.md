Kailash Balakrishnan
101108563

# carleton-profs
Scraping Data of all professors in Carleton's SCS,SCE,IT and Math Department using python and BeautifulSoup4

The project repo can be found on [GitHub](https://github.com/Kailinho/carleton-profs).


Instructions to run the program(s):
Navigate to the folder containing the required scripts.
Run the command `python script.py` in a terminal replacing `script` with the required faculty.
Each script will output a JSON file containing the required data.


Insctructions to clean the data:
There are a few cases where the scraping results in empty keys and some unnecessary data. 
Navigate to the required JSON, and search "" and " ", removing any empty keys that are present. The existence of these empty keys will prevent the JSON's upload to firebase.
Search for any of "Facebook/Twitter/Share" and remove fields that are usually footers. A couple of professors' data includes this due to outliers in the homepage HTML structure. 

Combine the 4 JSON's in any way you like. I further used `https://codeshack.io/json-sorter/` to sort the combined JSON by name.