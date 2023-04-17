import json
import logging

import requests as requests
from bs4 import BeautifulSoup, Tag, SoupStrainer

log_format = '%(name)s : %(levelname)s : %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Scrapper')
logger.setLevel(logging.DEBUG)

BASE_URL = "https://www.csit.carleton.ca/index.php?pageID=PeopleFaculty"
BASE_PIC_URL = 'https://www.csit.carleton.ca/'
HEADER = {'Accept-Language': 'en-US',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

# Get person's contact information
def get_person_info_li(table_info: Tag):
    #Get Person's info from the table. Storing it as a dictionary as contact info is stored under a list.
    result = {}
    try:
        table = table_info.find_all('li')
        for i, li in enumerate(table):
            if i == 4:
                break
            if link := li.find('a'):
                result.update({li['class'][0]: link['href']})
            else:
                result.update({li['class'][0]: li.text})
    except AttributeError:
        return None

    return result

# Get person's research information and their data
def get_person_blob_info(person_article: Tag) -> []:
    result = {}
    try:
        # find all the titles
        titles = person_article.find_all(['h2', 'h3'])
        for title in titles:
            # find the big data list
            big_data: Tag = title.find_next_sibling('p').find_next_sibling('ul')
            big_data_list = []
            for li in big_data.find_all('li'):
                big_data_list.append(li.text)
            # update the result dict with the big data list
            result.update({title.text: big_data_list})
            return result
    except AttributeError:
        return None

    return result




def get_person_info(url: str) -> {}:
    # Initialise an empty dictionary for our results
    result = {}
    # Make a request to the provided URL
    resp = requests.get(url, headers=HEADER)
    logger.debug(url)

    # Use BeautifulSoup to parse the HTML into a Python object
    person_article = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('main'))
    # Get the person's details
    person_detail = person_article.find("div", {"class": "profile-name-desktop"})
    # Get the person's picture URL
    person_pic = person_article.find("div", {"class" : "photo"} ).get('style').split("../")[1].replace("');", "")
    # Get the person's contact information
    person_contact = person_article.find("ul", {"class": "contact"})
    # Get the person's research details
    person_research = person_article.find_all("section")[1]

    # Add the person's name to the result
    result.update({"name": person_detail.select_one('h1').text})
    # Add the person's department to the result
    result.update({"department":"School of Information Technology"})
    # Add the person's URL to the result
    result.update({"url": url})
    # Add the person's title to the result
    result.update({"title": person_detail.select_one('p').text})
    result.update({"picture": BASE_PIC_URL + person_pic})
    result.update({"contacts": get_person_info_li(person_contact)})
    result.update({"research": get_person_blob_info(person_research)})
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



def get_faculty_people(faculty: Tag) -> []:
    #Gets the people cards from the faculty section of the page
    people_cards = faculty.find_all('a')
    return [(card['href']) for card in people_cards]
    
def get_faculties_list_with_links(soup: Tag) -> dict[str, Tag]:
    #Gets the list of faculty with their links
    result: dict[str, []] = {}
    h1_tags = soup.find_all("h1")
    for h1_tag in h1_tags:
        if h1_tag.text == "Faculty & Full-Time Instructors":
            section_tag = h1_tag.find_next("section")
            result = get_faculty_people(section_tag)
            break
    return result



def main():
    # get the HTML content from the base URL
    resp = requests.get(BASE_URL, headers=HEADER)

    # create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('main'))
    # log the number of items found in the main tag
    logger.info(f"{len(soup)=}")

    # get the list of faculties with links
    faculties_with_links = get_faculties_list_with_links(soup)

    # create the output file
    with open('it.json', 'w', encoding="utf-8") as f:
        # create a list to store all the faculty information
        faculty_data = []
        # go through each link in the list of faculty links
        for link in faculties_with_links:
            # get the information for the faculty from the link
            faculty_data.append(get_person_info(link))
        # write the faculty data to the output file
        json.dump(faculty_data, f, indent=4 ,ensure_ascii=False)



if __name__ == '__main__':
    main()