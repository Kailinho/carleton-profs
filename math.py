import json
import logging

import requests as requests
from bs4 import BeautifulSoup, Tag, SoupStrainer

log_format = '%(name)s : %(levelname)s : %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Scrapper')
logger.setLevel(logging.DEBUG)

BASE_URL = "https://carleton.ca/math/our-people/faculty-members/"
HEADER = {'Accept-Language': 'en-US',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}


def get_person_table_info(table_info: Tag):
    result = {}
    try:
        table = table_info.find('table', {"class": "people__table"}).select_one('tbody')
        for row in table.find_all('tr'):
            row_value_cell: Tag = row.find('td', {"class": "people__table-info"})
            if link := row_value_cell.find('a'):
                value = link['href']
            else:
                value = row_value_cell.text
            result.update({row.find('td', {"class": "people__table-title"}).text: value})
    except AttributeError:
        return None

    return result


def get_person_blob_info(person_article: Tag) -> dict:
    result = {}
    try:
        strong_tags = person_article.find_all('strong')
        for strong_tag in strong_tags:
            title = strong_tag.text.strip()
            big_data = strong_tag.parent.text.replace(title, '').strip()
            result.update({title: big_data})
    except AttributeError:
        return None

    return result



def get_person_info(url: str) -> {}:
    result = {}
    resp = requests.get(url, headers=HEADER)
    logger.debug(url)
    person_article = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('article'))

    person_detail = person_article.find("div", {"class": "people__details"})
    person_picture = person_article.find("div",{"class": "people__photo"} )


    result.update({"name": person_detail.select_one('h2').text})
    result.update({"department":"School of Mathematics and Statistics"})
    result.update({"url": url})
    result.update({"title": person_detail.select_one('p').text})
    picture = person_picture.select_one('img')['src'] if person_picture else""
    result.update({"picture": picture})
    result.update({"contacts": get_person_table_info(person_detail)})
    result.update({"research": get_person_blob_info(person_article)})

    research_info = result['research']
    research_data = ''
    for key, value in research_info.items():
        research_data += value 
    result.update({"research_data": research_data})

    return result


def get_faculty_people(faculty: Tag) -> []:
    people_cards = faculty.find_all('a')
    return [card['href'] for card in people_cards]


def get_faculties_list_with_links(soup: Tag) -> dict[str, Tag]:
    result: dict[str, []] = {}
    section = soup.find("section")
    result = get_faculty_people(section)
    return result



def main():
    resp = requests.get(BASE_URL, headers=HEADER)

    soup = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('article'))
    logger.info(f"{len(soup)=}")

    faculties_with_links = get_faculties_list_with_links(soup)

    # for link in faculties_with_links:
    #     print(json.dumps(get_person_info(link), indent=4))


    with open('mathfaculty.json', 'w', encoding="utf-8" ) as f:
        faculty_data = []
        for link in faculties_with_links:
            faculty_data.append(get_person_info(link))
        json.dump(faculty_data, f, indent=4, ensure_ascii=False)



if __name__ == '__main__':
    main()