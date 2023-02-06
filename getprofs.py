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
                profName = driver.find_element(By.CSS_SELECTOR,"article").find_element(By.CLASS_NAME,"people__heading").get_attribute("innerHTML")
                profWebsite = driver.find_element(By.CSS_SELECTOR,"article").find_element(By.XPATH,"//td[text()='Website:']/following-sibling::td").find_element(By.CSS_SELECTOR,"a").get_attribute("href")
                researchInterests = driver.find_element(By.CSS_SELECTOR,"article").find_element(By.XPATH,"//h3[text()='Research Interests']/following-sibling::p").get_attribute("innerHTML")
                specificResearchInterests = driver.find_element(By.CSS_SELECTOR,"article").find_element(By.XPATH,"//h3[text()='Specific Research Interests']/following-sibling::p").get_attribute("innerHTML")

        except (NoSuchElementException,AttributeError,IndexError):
                profWebsite = "No Website"
                researchInterests = "No Research Interests"
                specificResearchInterests = "No Specific Research Interests"

        data.append([url1, profName, profWebsite, researchInterests, specificResearchInterests])

df = pd.DataFrame(data,columns=["Scraped Url", "Name","Website Url","Research Interests","Specific Research Interests"])
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

#         info1 = doc1.select_one("h3", text="Research Interests")
#         if info1:
#                 researchInterests = info1.find_next_sibling("p").text
#         else:
#                 info1 = "No Research Interests"
#                 researchInterests = "No Research Interests"

#         info2 = doc1.select_one("h3", string="Specific Research Interests")
#         if info2:
#                 specificResearchInterests = info2.find_next_sibling("p").string
#         else:
#                 info2 = "No Specific Research Interests"
#                 specificResearchInterests = "No Specific Research Interests"

#         # info3 = doc1.select_one("article > p:nth-of-type(3):not(.content__metadata):not(.content__meta) a").text.strip()
#         # info4 = doc1.select_one("article > p:nth-of-type(4):not(.content__meta):not(.content__meta) a").text.strip()
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