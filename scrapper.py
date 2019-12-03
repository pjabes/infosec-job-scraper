import requests
from bs4 import BeautifulSoup
import logging
import logging.config
import yaml
import pandas as pd
import numpy as np



with open('./conf/logs.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)
logger.debug('script started')
logger.debug('logging started')

def getJobLinks(page):

    baseURL = "https://au.indeed.com"
    logger.debug('getJobLinks() called page=%s, baseURL=%s', page, baseURL)
    logger.debug('attempting to download source for %s', page)
    source = requests.get(page).text
    soup = BeautifulSoup(source, 'html.parser')

    if soup:
        logger.debug('successfully downloaded %s', page)
    else:
        logger.info('unsuccessful attempt at downloading %s', page)
        exit()

    jobLinks = soup.find_all('a', attrs={'class': 'jobtitle'})

    if jobLinks:
        for link in jobLinks:
            cleanString = str(baseURL) + link['href']
            cleanString = cleanString.strip('&jvs=3')
            logger.info('found job: %s', cleanString)
    else:
        logger.info('unable to extract jobs')
    
    # TODO:  Save these jobLink results

    return jobLinks

def getJobInformation(url):
    logger.debug('getJobInformation() called for url=%s', url)

    logger.debug('attempting to download %s', url)
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')
    if soup:
        logger.debug('successfully downloaded %s', url)
    else:
        logger.info('unsuccessful attempt at downloading %s', url)
        exit()


    # TODO:  Terrible code - this desperately needs optimisation...
    jobTitle = soup.find('h3', attrs={'class': 'jobsearch-JobInfoHeader-title'})
    
    if jobTitle:
        jobTitle = jobTitle.text
    else:
        jobTitle = '-'

    jobCompanyName = soup.find('a', attrs={'class': 'jobsearch-CompanyAvatar-companyLink'})

    if jobCompanyName:
        jobCompanyName = jobCompanyName.text
    else:
        jobCompanyName = '-'

    jobLocation = soup.find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})

    if jobLocation:
        jobLocation = jobLocation.text
    else:
        jobLocation = '-'

    jobPeriod = soup.find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})

    if jobPeriod:
        jobPeriod = jobPeriod.text
    else:
        jobPeriod = '-'


    jobPostDate = soup.find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})

    if jobPostDate:
        jobPostDate = jobPostDate.text
    else:
        jobPostDate = '-'

    jobSalary = soup.find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})

    if jobSalary:
        jobSalary = jobSalary.text
    else:
        jobSalary = '-'

    jobDescription = soup.find('div', attrs={'class': 'jobsearch-jobDescriptionText'})

    if jobDescription:
        jobDescription = jobDescription.text 
    else:
        jobDescription = '-'    


    DataDict = {
        'jobTitle': jobTitle,
        'jobCompanyName': jobCompanyName,
        'jobLocation': jobLocation,
        'jobPeriod': jobPeriod,
        'jobSalary': jobSalary,
        'jobDescription': jobDescription,
        'jobPostDate': jobPostDate
    }

    df = pd.DataFrame(DataDict, index=[0])
    return df 

getJobInformation('https://au.indeed.com/rc/clk?jk=4d0142c2704ceffb&fccid=dd09fe3b43125016&vjs=3')

# getJobLinks("https://au.indeed.com/jobs?q=Cyber+Security+&l=Melbourne+VIC")
