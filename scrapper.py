import requests
from bs4 import BeautifulSoup
import logging
import logging.config
import yaml
import pandas as pd
import numpy as np
import urllib.parse
import re
from datetime import datetime, timedelta
import time

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
    cleanJobs = []

    if jobLinks:
        for link in jobLinks:
            cleanString = str(baseURL) + link['href']
            cleanString = cleanString.strip('&jvs=3')
            logger.info('found job: %s', cleanString)
            cleanJobs.append(cleanString)
    else:
        logger.info('unable to extract jobs')
    
    # TODO:  Save these jobLink results

    for job in cleanJobs:
        logger.info('--- kicking off jobExtraction for %s', job)
        getJobInformation(job)
        logger.info('sleeping for 2')
        time.sleep(2)

    return cleanJobs

def getJobInformation(url):

    if "/pagead/" in url:
        pass
    else:
        logger.debug('getJobInformation() called for url=%s', url)

        jobID = urllib.parse.parse_qs(url)['https://au.indeed.com/rc/clk?jk'][0]
        url = 'https://au.indeed.com/viewjob?jk=' + str(jobID)
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
        metaScrapeDatetime = datetime.today()

        
        if jobTitle:
            jobTitle = jobTitle.text
        else:
            jobTitle = '-'

        try:
            jobCompanyName = soup.find('div', attrs={'class': 'jobsearch-InlineCompanyRating'}).find('div', attrs={'class': 'icl-u-lg-mr--sm icl-u-xs-mr--xs'})
        except:
            jobCompanyName = False

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
            # TODO:  Will need to capture this differently - what happens if the company contains numbers?
            daysAgo = int(re.findall('[0-9][0-9]*', jobPostDate.text)[-1])
            if daysAgo == 30:
                jobPostDate = '-'
            else:
                jobPostDate = (datetime.today() - timedelta(days=daysAgo)).date()

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
            jobDescription = str(jobDescription.text)
        else:
            jobDescription = '-'    

        jobExternalLink = soup.find('a', text="original job")
        if jobExternalLink:
            jobExternalLink = jobExternalLink['href']
            jobExternalLink = requests.get(jobExternalLink, allow_redirects=True)
            jobExternalLink = jobExternalLink.url

        else:
            jobExternalLink = '-'

        logger.debug('created data dictionary with these values,')
        DataDict = {
            'jobID': jobID,
            'jobTitle': jobTitle,
            'jobCompanyName': jobCompanyName,
            'jobLocation': jobLocation,
            'jobPeriod': jobPeriod,
            'jobSalary': jobSalary,
            'jobDescription': jobDescription,
            'jobPostDate': jobPostDate,
            'jobExternalLink': jobExternalLink,
            'metaScrapeDatetime': metaScrapeDatetime,
        }
        
        df = pd.DataFrame(DataDict, index=[0])
        print(df)
        df.to_csv('jobs.csv', mode='a', header=False)
        logger.debug('appended data to jobs.csv')
        return df 

# getJobInformation('https://au.indeed.com/viewjob?cmp=JSB-Security&t=Security+Officer&jk=314e09e3845f5f5f&sjdu=8EWtruxy728tzxKcUmN0cSZVzcxIQSQJRLjqibOOMsTn30d0H9nOP49Hqk2_X4fn2ddok_-sIGEq2-Xe_CA93A&tk=1dsjti08r82gi801&adid=323207836&pub=4a1b367933fd867b19b072952f68dceb&vjs=3')

getJobLinks("https://au.indeed.com/Cyber-Security-jobs-in-Melbourne-VIC")
