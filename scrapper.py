import requests
from bs4 import BeautifulSoup
import logging
import logging.config
import yaml
import pandas as pd
import numpy as np
import urllib.parse
import re

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

    jobID = urllib.parse.parse_qs(url)['jk']
    jobTitle = soup.find('h3', attrs={'class': 'jobsearch-JobInfoHeader-title'})
    

    
    if jobTitle:
        jobTitle = jobTitle.text
    else:
        jobTitle = '-'

    jobCompanyName = soup.find('div', attrs={'class': 'jobsearch-InlineCompanyRating'}).find('div', attrs={'class': 'icl-u-lg-mr--sm icl-u-xs-mr--xs'})

    if jobCompanyName:
        jobCompanyName = jobCompanyName.text
    else:
        jobCompanyName = '-'
    try:
        jobLocation = soup.find('div', attrs={'class': 'icl-IconFunctional--location'}).find_parent().find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})
    except:
        jobLocation = False
    if jobLocation:
        jobLocation = jobLocation.text
    else:
        jobLocation = '-'
    try:
        jobPeriod = soup.find('div', attrs={'class': 'icl-IconFunctional--jobs'}).find_parent().find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})
    except:
        jobPeriod = False
    if jobPeriod:
        jobPeriod = jobPeriod.text
    else:
        jobPeriod = '-'

    jobPostDate = soup.find('div', attrs={'class': 'jobsearch-JobMetadataFooter'})

    if jobPostDate:
        jobPostDate = re.findall(r'[0-9]*', jobPostDate.text)
        
        print(jobPostDate)
    else:
        jobPostDate = '-'
    try:
        jobSalary = soup.find('div', attrs={'class': 'icl-IconFunctional--salary'}).find_parent().find('span', attrs={'class': 'jobsearch-JobMetadataHeader-iconLabel'})
    except:
        jobSalary = False
    if jobSalary:
        jobSalary = jobSalary.text
    else:
        jobSalary = '-'

    jobDescription = soup.find('div', attrs={'class': 'jobsearch-jobDescriptionText'})

    if jobDescription:
        jobDescription = jobDescription.text 
    else:
        jobDescription = '-'    

    jobExternalLink = soup.find('a', text="original job")
    if jobExternalLink:
        jobExternalLink = jobExternalLink['href']
    else:
        jobExternalLink = '-'

    jobHash = hash(jobTitle + jobCompanyName)

    DataDict = {
        'jobID': jobID,
        'jobTitle': jobTitle,
        'jobCompanyName': jobCompanyName,
        'jobLocation': jobLocation,
        'jobPeriod': jobPeriod,
        'jobSalary': jobSalary,
        'jobDescription': jobDescription,
        'jobPostDate': jobPostDate,
        'jobExternalLink': jobExternalLink
    }
    
    df = pd.DataFrame(DataDict, index=[0])
    print(df)
    return df 

getJobInformation('https://au.indeed.com/viewjob?cmp=JSB-Security&t=Security+Officer&jk=314e09e3845f5f5f&sjdu=8EWtruxy728tzxKcUmN0cSZVzcxIQSQJRLjqibOOMsTn30d0H9nOP49Hqk2_X4fn2ddok_-sIGEq2-Xe_CA93A&tk=1dsjti08r82gi801&adid=323207836&pub=4a1b367933fd867b19b072952f68dceb&vjs=3')

# getJobLinks("https://au.indeed.com/jobs?q=Cyber+Security+&l=Melbourne+VIC")
