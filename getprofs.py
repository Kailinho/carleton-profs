from bs4 import  BeautifulSoup
import requests
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from lxml import etree


url = f"https://carleton.ca/scs/our-people/school-of-computer-science-faculty/"



#Code using Selenium, comment out the code until line 46 to use beautifulsoup instead

PATH = Service("C:\Program Files (x86)\chromedriver.exe")
driver = webdriver.Chrome(service=PATH)
driver.get(url)
links = driver.find_elements(By.CLASS_NAME,"card__link")
profLinks = []

#Get all profs' links from main scs page
for eachLink in links:
        profLinks.append(eachLink.get_attribute("href"))

data = []  
for url1 in profLinks:
        try:

                driver.get(url1)
                article = driver.find_element(By.XPATH,"//article[@role='article']")
                children = article.find_elements(By.XPATH,"./*[(self::div or self::h3 or self::p) and not(contains(@class, 'content__metadata')) and not(contains(@class, 'content__meta'))]")
                profName = driver.find_element(By.CSS_SELECTOR,"article").find_element(By.CLASS_NAME,"people__heading").get_attribute("innerHTML")
                # profWebsite = driver.find_element(By.CSS_SELECTOR,"article").find_element(By.XPATH,"//td[text()='Website:']/following-sibling::td").find_element(By.CSS_SELECTOR,"a").get_attribute("href")
                print(profName)
                for child in children:
                        child_data= {}
                        # child_data["Name"] = profName
                        # child_data["Website"] = profWebsite                        
                        tag_name = child.tag_name
                        href = child.get_attribute("href")
                        inner = child.get_attribute("innerHTML")
                        text = child.get_attribute("textContent")

                        if tag_name == "h3":
                                child_data["Key"] = inner
                                print(inner)
                        elif tag_name == "p":
                                child_data["Value"] = inner
                                print(inner)

                        data.append(child_data)
                        # elif tag_name =="a":
                        #         print("Link: ",href)


        except (NoSuchElementException,AttributeError,IndexError,NameError):
                
                print(NoSuchElementException)
                print(AttributeError)
                print(IndexError)
                print(NameError)

        # data.append([url1, profName, profWebsite, researchInterests, specificResearchInterests])

df = pd.DataFrame(data)
df.to_csv("scsprofs.csv", index=False)














#Code using Beautifulsoup

# page = requests.get(url).text
# doc = BeautifulSoup(page, "html.parser")
# sections = doc.find("section")
# profsUrl = sections.find_all("a",limit = 45,class_="card__link")
# profLinks = []


# for profUrl in profsUrl:
#         profLinks.append(profUrl.get("href"))


# data = []
# for url1 in profLinks:
#     page1 = requests.get(url1).text
#     doc1 = BeautifulSoup(page1, "html.parser")
#     try:
#         headline = doc1.find("h2",class_="people__heading").string
#         websiteTitle = doc1.select_one("tr:-soup-contains('Website:') a").text
#         websiteUrl = doc1.select_one("tr:-soup-contains('Website:') a").get("href")

#         info1 = doc1.select_one("h3", string=re.compile(r'^Research Interests$'))
#         if info1:
#                 researchInterests = info1.find_next_sibling("p").text
#         else:
#                 # info1 = "No Research Interests"
#                 researchInterests = "No Research Interests"

#         info2 = doc1.select_one("h3", string=re.compile(".*Specific Research Interests*"))
#         if info2:
#                 specificResearchInterests = info2.find_next_sibling("p").string
#         else:
#                 # info2 = "No Specific Research Interests"
#                 specificResearchInterests = "No Specific Research Interests"


#     except (AttributeError,IndexError):

#         websiteTitle = "No website title"
#         websiteUrl = "No website"
#         info1 = "No Research Interests"
#         researchInterests = "No Research Interests"
#         info2 = "No Specific Research Interests"
#         specificResearchInterests = "No Specific Research Interests"

#     print(headline)
#     data.append([url1,headline, websiteTitle, websiteUrl, researchInterests, specificResearchInterests])


# df = pd.DataFrame(data,columns=["Scraped Url", "Name","Website Title","Website Url","Research Interests","Specific Research Interests"])
# df.to_csv("scsprofs.csv", index=False)

# Current Research, Research Group, Homepage , ORCID