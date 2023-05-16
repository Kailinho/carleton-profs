import json
import logging

import requests as requests
from bs4 import BeautifulSoup, Tag, SoupStrainer

log_format = '%(name)s : %(levelname)s : %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Scrapper')
logger.setLevel(logging.DEBUG)

BASE_URL = "https://carleton.ca/cognitivescience/staff-and-faculty/faculty/"
HEADER = {'Accept-Language': 'en-US',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

# Get person's contact information
def get_person_table_info(table_info: Tag):
    # Create a dictionary to store the result
    result = {}
    try:
        # Find the table
        table = table_info.find('table', {"class": "people__table"}).select_one('tbody')
        for row in table.find_all('tr'):
            # Get the value cell
            row_value_cell: Tag = row.find('td', {"class": "people__table-info"})
            # If the value is a link, get the link
            if link := row_value_cell.find('a'):
                value = link['href']
            # Otherwise, get the text
            else:
                value = row_value_cell.text
            # Store the result in the dictionary
            result.update({row.find('td', {"class": "people__table-title"}).text: value})
    # If table_info is None, return None
    except AttributeError:
        return None

    return result

def get_person_blob_info(person_article: Tag) -> dict:
    result = {}
    try:
        titles = person_article.find_all(['h4','p','h2','h3'])
        all_text = ""
        for title in titles:
            if not ( any(parent.has_attr('class') and ('people__photo' in parent['class'] or 'people__details' in parent['class'] or 'content__meta' in parent['class'] or 'content__metadata' in parent['class']) for parent in title.parents) or ( (title.has_attr('class')) and ('content__meta' in title['class'] or 'content__metadata' in title['class']  ) )):
               all_text += title.text + "\n"            
        result.update({"research": all_text})
    except AttributeError:
        return None
    return result




# Get the data for each person
def get_person_info(url: str) -> {}:
    # Create a dictionary to store the result
    result = {}
    resp = requests.get(url, headers=HEADER)
    logger.debug(url)
    person_article = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('article'))

    # Find the divs with the person details and picture, which will be further used to get the data
    person_detail = person_article.find("div", {"class": "people__details"})
    person_picture = person_article.find("div",{"class": "people__photo"} )


    # Get the name, department, title, picture, contacts and research info
    result.update({"name": person_detail.select_one('h2').text})
    # get the person's department
    result.update({"department":"School of Geography and Environmental Studies"})
    # get the person's url
    result.update({"url": url})
    # get the person's title
    result.update({"title": person_detail.select_one('p').text})
    # get the person's picture
    result.update({"picture": person_picture.select_one('img')['src']})
    # get the person's contacts
    result.update({"contacts": get_person_table_info(person_detail)})
        #get the person's research information
    result.update({"research": get_person_blob_info(person_article)})

    # Concatenate the research info into a single string, to be used in the search engine to improve efficiency
    research_data = ""
    # Get the value of the 'research' key from the result dictionary
    research_dict = result.get("research")

    # If the value of the 'research' key is not None and is a dictionary
    if research_dict:
        # Loop through the key-value pairs of the 'research' dictionary
        for key, value in research_dict.items():
            # If the value of the current key is a list
            if isinstance(value, list):
                # Join all the items in the list with a newline character and add it to research_data
                research_data += "\n".join(value)
                # Add two newlines to research_data
                research_data += "\n\n"
            else:
                # Add the key and value to research_data and add two newlines
                research_data += f"{key}: {value}\n\n"
        # Update the result dictionary with the new research_data key and value
        result.update({"research_data": research_data})

    return result


# Get the list of people for each faculty
def get_faculty_people(faculty: Tag) -> []:
    # Find all the people cards and get the link for each one
    people_cards = faculty.find_all('a')
    return [card['href'] for card in people_cards]

def get_faculties_list_with_links(soup: Tag) -> dict[str, Tag]:
    result: dict[str, []] = {}
    tag = soup.find("section")
    result = get_faculty_people(tag)
    return result


def main():
    resp = requests.get(BASE_URL, headers=HEADER)
    #Beautifulsoup object with only the relevant article tag 
    soup = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('main'))

    logger.info(f"{len(soup)=}")
    #Get the list of faculties with their links
    faculties_with_links = get_faculties_list_with_links(soup)
    #Get the data for each faculty
    with open('cog.json', 'w', encoding="utf-8") as f:
        faculty_data = []
        for link in faculties_with_links:
            faculty_data.append(get_person_info(link))
        json.dump(faculty_data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()