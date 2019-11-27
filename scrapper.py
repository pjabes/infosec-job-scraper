import requests
from bs4 import BeautifulSoup

print('BeautifulSoup4 Imported')

def getJobLinks(page):
    print('getJobLinks - STARTED')
    source = requests.get(page).text
    soup = BeautifulSoup(source, 'html.parser')

    links = soup.find_all('a', attrs={'class': 'jobtitle'})


    for link in links:

        baseURL = "https://au.indeed.com"
        print(str(baseURL) + str(link['href'])) 

def getJobInformation(url):
    print('getJobInformation - STARTED')

    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')



    jobTitle = soup.find('h3', attrs={'class': 'jobsearch-JobInfoHeader-title'}).text
    jobLocation = soup.find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'}).text
    jobDescription = soup.find('div', attrs={'class': 'jobsearch-jobDescriptionText'}).text


    print(jobTitle)
    print(jobLocation)
    print(jobDescription)


getJobInformation('https://au.indeed.com/rc/clk?jk=4d0142c2704ceffb&fccid=dd09fe3b43125016&vjs=3')

# getJobLinks("https://au.indeed.com/jobs?q=Cyber+Security+&l=Melbourne+VIC")
