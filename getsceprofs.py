
import json
import logging

import requests as requests
from bs4 import BeautifulSoup, Tag, SoupStrainer

log_format = '%(name)s : %(levelname)s : %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Scrapper')
logger.setLevel(logging.DEBUG)

BASE_URL = "https://carleton.ca/sce/faculty/"
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
        titles = person_article.find_all('h4')
        for title in titles:
            big_data = []
            next_el = title.find_next()
            while next_el:
                if next_el.name in ['ul', 'p']:
                    if next_el.name == 'ul':
                        for li in next_el.find_all("li"):
                            if li.ul:
                                for sub_li in li.ul.find_all("li"):
                                    big_data.append(sub_li.text)
                            else:
                                big_data.append(li.text)
                    elif next_el.name == 'p' :
                        big_data.append(next_el.text)
                if next_el.name == 'h4':
                    break
                next_el = next_el.find_next()
            result.update({title.text: big_data})
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
    result.update({"title": person_detail.select_one('p').text})
    picture = person_picture.select_one('img')['src'] if person_picture else""
    result.update({"picture": picture})
    result.update({"contacts": get_person_table_info(person_detail)})
    result.update({"research": get_person_blob_info(person_article)})
    return result


def get_faculty_people(faculty: Tag) -> []:
    people_cards = faculty.find_all('a')
    return [card['href'] for card in people_cards]


def get_faculties_list_with_links(soup: Tag) -> dict[str, Tag]:
    result: dict[str, []] = {}
    h3_tags = soup.find_all("h3")
    for h3_tag in h3_tags:
        if h3_tag.text == "Faculty":
            section_tag = h3_tag.find_next("section")
            result = get_faculty_people(section_tag)
            break
    return result



def main():
    resp = requests.get(BASE_URL, headers=HEADER)

    soup = BeautifulSoup(resp.content, 'html.parser', parse_only=SoupStrainer('article'))
    logger.info(f"{len(soup)=}")

    faculties_with_links = get_faculties_list_with_links(soup)

    with open('scefaculty.json', 'w') as f:
        faculty_data = []
        for link in faculties_with_links:
            faculty_data.append(get_person_info(link))
        json.dump(faculty_data, f, indent=4)
    # for link in faculties_with_links:
    #     print(json.dumps(get_person_info(link), indent=4))


if __name__ == '__main__':
    main()