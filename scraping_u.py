from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import numpy as np
from selenium import webdriver
import os

my_url = 'https://www.avanza.se/aktier/lista.html'

#opening up connection, grabbing the page
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# html parsing
page_soup = soup(page_html, "html.parser")

# grabs the choosing box of börsvärde & listor
choosing_box = page_soup.findAll("div", {"class":"category"})
box_2 = page_soup.findAll("div", {"class":"component landFilter"})


# browser = webdriver.PhantomJS()
# browser.get("https://www.python.org/")
# print(browser.find_element_by_class_name("introduction").text)
# browser.close()



# browser.find_element_by_id("C179003030-ORNL_DAAC-box").click()
# print(box_2)
# company_table = page_soup.findAll("div", {"class":"ellipsis"})
# print(company_table)
companyList = []
companyDataRaw = []
companyNames = []
omBolagen = []
omBolagetData = []
chosenCompanies = []
headers = np.array([["Namn"], ["Kortnamn(ticker)"], ["Datum för redovisning"], ["Börsvärde"], ["Direktavkastning"], ["P/E-tal"], ["P/S-tal"], ["Vinst/aktie"], ["Antal ägare(Avanza)"], ["Räntabilitet EK"], ["Soliditet"], ["Rörelsemarginal"], ["Årets resultat"]])
enterpriseData = []

#Get companies links
def get_company_links():
    global chosenCompanies
    for link in page_soup.findAll('a', attrs={"class" : "ellipsis"} ):
        httpsString = "https://www.avanza.se"
        link['href'] = httpsString + link['href']
        # Extract all companies
        mylink = link.get('href')
        companyList.append(mylink)
    # print(companyList)
    # print(len(companyList))
    chosenCompanies = companyList[0:1]



def get_Om_aktien():
    global companyDataRaw
    global companyNames
    global omBolagen
    global chosenCompanies
    oneCompanyData = []
    for company in chosenCompanies:
        uClient = uReq(company)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        full_name = page_soup.find('h1', attrs={"class" :
                                    "large marginBottom10px"}).text
        full_name = re.sub(r'[\W_]+', '', full_name)
        companyNames.append(full_name)
        span = ''
        for spans in page_soup.findAll(["div", "span"], attrs={"class":"column grid_3point5"}):
            # Removes <span> & <dd>/<dt>
            # print(spans)
            span += spans.text.strip()
        dataArray = span.split()
        # print("index: " + str(oneCompany.index(company)))
        companyDataRaw.append([dataArray][0])
        om_bolagen = page_soup.findAll(href=re.compile("/aktier/om-bolaget"))
        om_bolagen = str(om_bolagen)
        #om_bolaget = re.sub('^(.*)(?=href)', '', om_bolaget)
        om_bolagen = 'https://www.avanza.se' + om_bolagen[10:-17]
        omBolagen.append(om_bolagen)


def put_into_matrix():
    global enterpriseData
    global headers
    global companyDataRaw
    global companyNames
    global omBolagetData
    # print("len datatarrray: " + str(len(dataArray)))
    # print(dataArray)
    for company in range(len(companyDataRaw)):
        dataArray = companyDataRaw[company]
        # print("DATA ARRAY: " + str(dataArray))
        #Delete previous numbers that now are grouped together
        previous = "@"
        numbers_to_delete = []
        for index in range(len(dataArray)-1):
            concatinate = ''
            # print("index: " + str(index))
            if dataArray[index][0].isdigit():
                # print("digit detetcted: " + str(dataArray[index]))
                if previous.isdigit():
                    concatinate = previous + dataArray[index]
                    dataArray[index] = concatinate
                    numbers_to_delete.append(index-1)
            previous = dataArray[index]
        # print(dataArray)
        #reversing the list
        numbers_to_delete.reverse()
        # print(numbers_to_delete)
        for index in range(len(numbers_to_delete)):
            dataArray.pop(numbers_to_delete[index])
            # print("popped: " + str(numbers_to_delete[index]))

        # print(dataArray)
        # print("Length: " + str(len(dataArray)))

        #Get the data into arrays
        index = dataArray.index("Kortnamn")+1
        ticker = dataArray[index]
        index = dataArray.index("Börsvärde")+2
        borsvarde = dataArray[index]
        index = dataArray.index("Direktavkastning")+2
        direktavkastning = dataArray[index]
        index = dataArray.index("P/E-tal")+1
        PE = dataArray[index]
        index = dataArray.index("P/S-tal")+1
        PS = dataArray[index]
        index = dataArray.index("Vinst/aktie")+2
        vinstPAktie = dataArray[index]
        index = dataArray.index("ägare")+3
        agare = dataArray[index]
        index = omBolagetData[company].index("Datum")+3
        datum = omBolagetData[company][index]
        index = omBolagetData[company].index("Räntabilitet")+4
        rantabilitetEK = omBolagetData[company][index]
        index = omBolagetData[company].index("Soliditet")+2
        soliditet = omBolagetData[company][index]
        index = omBolagetData[company].index("Rörelsemarginal")+2
        rorelsemarginal = omBolagetData[company][index]
        index = omBolagetData[company].index("Årets")+2
        resultat = omBolagetData[company][index]
        # thisCompanyData = np.array([[companyNames[company]], [ticker], [datum], [borsvarde], [direktavkastning], [PE], [PS], [vinstPAktie], [agare], [rantabilitetEK], [soliditet], [rorelsemarginal], [resultat]])
        thisCompanyData = np.array([companyNames[company], ticker, datum, borsvarde, direktavkastning, PE, PS, vinstPAktie, agare, rantabilitetEK, soliditet, rorelsemarginal, resultat])
        
        print(thisCompanyData)
        thisCompanyData = np.transpose(thisCompanyData)
        print("thisCompanyData " + str(thisCompanyData)+'\n')
        # print(thisCompanyData)
        headers = np.transpose(headers)
        print("headers "+ str(headers) + '\n')
        print("enterpriseData " + str(enterpriseData) + '\n')
        if len(enterpriseData) == 0:
            enterpriseData = np.append(headers, thisCompanyData, axis=0)
        else:
            enterpriseData = np.append(enterpriseData, thisCompanyData, axis=0)
    print("Enterprisedata " + str(enterpriseData))

def om_bolaget():
    global omBolagetData
    global omBolagen
    for bolag in range(len(omBolagen)):
        uClient = uReq(omBolagen[bolag])
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        dataArray = ''
        # Om aktien
        for dls in page_soup.findAll('dl', attrs={"class" : "border XSText rightAlignText noMarginTop highlightOnHover thickBorderBottom noTopBorder"}):
            dataArray += dls.text.strip()
        # Balansräkning
        for table in page_soup.findAll('table', attrs={"class" : ["dottedRows", "noRowHighlight", "RowHighligth"]}):
            dataArray += table.text.strip()
        # Resultaträkning
        for div in page_soup.findAll("div", attrs={"class" : "company_income_statement"}):
            dataArray += div.text.strip()

        dataArray = dataArray.split()
        # print(dataArray)
        omBolagetData.append(dataArray)

def put_into_csv():
    global enterpriseData
    listcompanies = os.path.join('/Users/Michael/Documents/Programmering/Python-projekt', 'listcompanies.csv')
    print('\n')
    print(enterpriseData)
    print(enterpriseData[[1]])
    # df = pd.DataFrame({enterpriseData})


get_company_links()
get_Om_aktien()
om_bolaget()
put_into_matrix()
put_into_csv()
