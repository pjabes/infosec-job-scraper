import requests
from bs4 import BeautifulSoup

print('BeautifulSoup4 Imported')

def getJobLinks(page):
    print('getJobLinks - STARTED')
    baseURL = "https:/au.indeed.com"
    source = requests.get(page).text
    soup = BeautifulSoup(source, 'html.parser')

    links = soup.find_all('a', attrs={'class': 'jobtitle'})


    for link in links:

        link
        print(str(baseURL) + str(link['href'])) 

getJobLinks("https://au.indeed.com/jobs?q=Cyber+Security+&l=Melbourne+VIC")
