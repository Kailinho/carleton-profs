from bs4 import  BeautifulSoup
import requests
import re
import pandas as pd

url = f"https://carleton.ca/scs/our-people/school-of-computer-science-faculty/"
page = requests.get(url).text
doc = BeautifulSoup(page, "html.parser")
sections = doc.find("section")
profsUrl = sections.find_all("a",limit = 45,class_="card__link")
profLinks = []


for profUrl in profsUrl:
        profLinks.append(profUrl.get("href"))


data = []
for url1 in profLinks:
    page1 = requests.get(url1).text
    doc1 = BeautifulSoup(page1, "html.parser")
    try:
        headline = doc1.find("h2",class_="people__heading").string
        websiteTitle = doc1.select_one("tr:-soup-contains('Website:') a").text
        websiteUrl = doc1.select_one("tr:-soup-contains('Website:') a").get("href")

        info1 = doc1.find("h3", string="Research Interests")
        if info1:
                researchInterests = info1.find_next_sibling("p").string
        else:
                info1 = "No Research Interests"
                researchInterests = "No Research Interests"

        info2 = doc1.find("h3", string="Specific Research Interests")
        if info2:
                specificResearchInterests = info2.find_next_sibling("p").string
        else:
                info2 = "No Specific Research Interests"
                specificResearchInterests = "No Specific Research Interests"

        # info3 = doc1.select_one("article > p:nth-of-type(3):not(.content__metadata):not(.content__meta) a").text.strip()
        # info4 = doc1.select_one("article > p:nth-of-type(4):not(.content__meta):not(.content__meta) a").text.strip()
    except (AttributeError,IndexError):
        # headline = "No name"
        websiteTitle = "No website title"
        websiteUrl = "No website"
        info1 = "No Research Interests"
        researchInterests = "No Research Interests"
        info2 = "No Specific Research Interests"
        specificResearchInterests = "No Specific Research Interests"

    print(headline)
    data.append([url1,headline, websiteTitle, websiteUrl, researchInterests, specificResearchInterests])
#     headline, websiteTitle, websiteUrl, researchInterests, specificResearchInterests = ""

df = pd.DataFrame(data,columns=["Scraped Url", "Name","Website Title","Website Url","Research Interests","Specific Research Interests"])
df.to_csv("scsprofs.csv", index=False)

