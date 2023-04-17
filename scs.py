import json
import logging

import requests as requests
from bs4 import BeautifulSoup, Tag, SoupStrainer

log_format = '%(name)s : %(levelname)s : %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Scrapper')
logger.setLevel(logging.DEBUG)

BASE_URL = "https://carleton.ca/scs/our-people/school-of-computer-science-faculty/"
HEADER = {'Accept-Language': 'en-US',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}


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


def get_person_blob_info(person_article: Tag) -> []:
    """
    Gets the blob information from the person article
    :param person_article: the article with the blob info
    :return: a list of dictionaries (one per blob) with the data
    """
    result = {}
    try:
        titles = person_article.find_all('h3')
        for title in titles:
            big_data: Tag = title.next_sibling
            while big_data.name != 'p' and ('content__meta' not in big_data.parent.get('class', []) and 'content__metadata' not in big_data.parent.get('class', [])):
                big_data = big_data.next_sibling
            result.update({title.text: big_data.text})
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
    result.update({"department":"School of Computer Science"})
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
    research_info = result['research']
    research_data = ''
    for key, value in research_info.items():
        research_data += value 
    result.update({"research_data": research_data})

    return result


# Get the list of people for each faculty
def get_faculty_people(faculty: Tag) -> []:
    # Find all the people cards and get the link for each one
    people_cards = faculty.find_all('a')
    return [card['href'] for card in people_cards]

# Get the list of faculties with their links
def get_faculties_list_with_links(soup: Tag) -> dict[str, Tag]:
    # Create a dictionary to store the result which will be a list of links for each faculty
    result: dict[str, []] = {}
    # Get the list of faculties from the article by finding all the h2 tags
    faculties: list[Tag] = soup.find_all("h2")
    for faculty in faculties:
        logger.info(f"{faculty.text}")
        # Get the section with the people 
        faculty_data: Tag = faculty.next_element
        while faculty_data.name != 'section':
            faculty_data = faculty_data.next_element
        # Call the function to get the list of people for each faculty
        result.update({faculty.text: get_faculty_people(faculty_data)})
    return result


def main():
    resp = requests.get(BASE_URL, headers=HEADER)
    #Beautifulsoup object with only the relevant article tag 
    soup = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('article'))
    logger.info(f"{len(soup)=}")
    #Get the list of faculties with their links
    faculties_with_links = get_faculties_list_with_links(soup)
    #Get the data for each faculty
    with open('scs.json', 'w', encoding="utf-8") as f:
        faculty_data = []
        counter = 0;
        for link in faculties_with_links['School Faculty']:
            faculty_data.append(get_person_info(link))
            counter += 1
        json.dump(faculty_data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()