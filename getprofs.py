from bs4 import  BeautifulSoup
import requests
import re

url = f"https://carleton.ca/scs/our-people/school-of-computer-science-faculty/"
page = requests.get(url).text
doc = BeautifulSoup(page, "html.parser")
sections = doc.find("section")
profsUrl = sections.find_all("a",limit = 45,class_="card__link")
profLinks = []


for profUrl in profsUrl:
        profLinks.append(profUrl.get("href"))



