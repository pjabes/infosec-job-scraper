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
from random import randint

with open('./conf/logs.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)
logger.debug('logging preferences successfully read in from ./conf/logs.yaml')


def extractJobID(url):
    """ Helper utility to extract JobID's from the URL.
    
    
    """
    
    try: 
        pattern = re.compile('jk=(.*?)&')
        return str(re.findall(pattern, url)[0])
    except:
        pattern = re.compile('jobs/.*-(.*?)\?')
        return str(re.findall(pattern, url)[0])

        logger.error('could not extract a jobid from url=%s', url)
        exit()


def extractNumberOfJobs(soup):
    """ Helper utility to extract numberOfJobs from BS4 soup object.


    """

    numberOfJobs = soup.find('div', attrs={'id': 'searchCountPages'}).text
    numberOfJobs = numberOfJobs.strip().split(' ')


    # 3'd element always contains the actual number of jobs, sometimes formatted with commas.
    return int(numberOfJobs[3].replace(',', ''))

def downloadPage(url):
    """ Helper utility to download a URL using the expected information.

        Returns:
            BeautifulSoup4 Object
    """
    logger.debug('downloadPage(): attempting to download %s', url)

    try:
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'html.parser')
        logger.debug('downloadPage(): successfully downloaded page')
        return soup
    except:
        logger.error('downloadPage(): unable to download %s', url)
        return None



def getJobLinks(page):

    baseURL = "https://au.indeed.com"

    logger.debug('getJobLinks(): called page=%s, baseURL=%s', page, baseURL)
    logger.debug('getJobLinks(): attempting to download source=%s', page)

    soup = downloadPage(page)
    if not soup:
        logger.info('getJobLinks(): unable to download the page')
        return 

    numberOfJobs = extractNumberOfJobs(soup)
    if not numberOfJobs:
        logger.error('getJobLinks(): unable to determine number of jobs')
        return 

    logger.info('getJobLinks(): Found a total number of %s jobs', str(numberOfJobs))

    cleanJobs = []
    jobsPerPage = 0

    while jobsPerPage < numberOfJobs:

        logger.info('getJobLinks(): scraping job links for batch %s of %s', jobsPerPage, numberOfJobs)

        url = page + '&start=' + str(jobsPerPage)


        soup = downloadPage(url)

        if not soup:
            logger.info('getJobLinks(): getJobLinks(): unable to download %s', url)
            return
 
        jobLinks = soup.find_all('a', attrs={'class': 'jobtitle'})
        logger.info('getJobLinks(): found %s jobs on the page', len(jobLinks))

        if jobLinks:
            for link in jobLinks:
                #TODO:  Handle Advertisements better

                if '/pagead/' in link['href']:
                    logger.info('getJobLinks(): found page advertisement, skipping these for now now')
                else:
                    cleanString = str(baseURL) + link['href']
                    logger.info('getJobLinks(): found jobID=%s', extractJobID(cleanString))
                    cleanJobs.append(cleanString)
                    getJobInformation(cleanString)

        else:
            logger.info('getJobLinks(): unable to extract jobs')

        randomSleep = randint(1,20)
        logger.info('getJobLinks(): sleeping for %s', str(randomSleep))
        time.sleep(randomSleep)


        jobLinks = []
        jobsPerPage += 10 

    logger.info('OPS:  Found %s jobs', len(cleanJobs))



    return cleanJobs

def getJobInformation(url):

    if "/pagead/" in url:
        pass
    else:
        logger.debug('getJobInformation(): called for url=%s', url)

        jobID = extractJobID(url)

        if str(jobID) in jobIDDict:
            logger.info('getJobInformation(): jobID %s matches previously seen before jobID', jobID)
            return 
        else:
            logger.info('getJobInformation(): jobID %s is a new job.', jobID)


            url = 'https://au.indeed.com/viewjob?jk=' + str(jobID)
            soup = downloadPage(url)

            if not soup:
                logger.info('getJobInformation(): unable to download %s', str(url))
                return

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
                try:
                    daysAgo = int(re.findall('[0-9][0-9]*', jobPostDate.text)[-1])
                    if daysAgo == 30:
                        jobPostDate = '-'
                    else:
                        jobPostDate = (datetime.today() - timedelta(days=daysAgo)).date()
                except:
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
                jobDescription = str(jobDescription.text)
            else:
                jobDescription = '-'    

            jobExternalLink = soup.find('a', text="original job")
            if jobExternalLink:
                jobExternalLink = jobExternalLink['href']
                try:
                    jobExternalLink = requests.get(jobExternalLink, allow_redirects=True)
                    jobExternalLink = jobExternalLink.url
                except:
                    jobExternalLink = '-'

            else:
                jobExternalLink = '-'

            logger.debug('getJobInformation(): created data dictionary with these values,')
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
                'metaScrapeURL': url 
            }
            
            df = pd.DataFrame(DataDict, index=[0])
            logger.info('getJobInformation(): jobID=%s, jobTitle=%s, jobCompany=%s...', jobID, jobTitle, jobCompanyName)
            df.to_csv('jobs.csv', mode='a', header=False, index=False)
            logger.debug('getJobInformation(): extracted job %s', jobID)
            return df 


def driver():
    logger.info('driver(): application logic starting')

    searchKeywords = ['cyber+security', 'information+security', 'cybersecurity', 'infosec', 'security', 'security+consultant', 'security+engineer', 'risk+management', 'grc']

    logger.info('driver(): populating jobID hashmap')

    # Preparing dictionary for hashmap
    jobs_df = pd.read_csv('./jobs.csv', names=['jobID', 'jobTitle', 'jobCompanyName', 'jobLocation', 'jobPeriod', 'jobSalary', 'jobDescription', 'jobPostDate', 'jobExternalLink', 'metaScrapeDatetime', 'metaURL'])
    global jobIDDict
    jobIDDict = {}
    
    jobIDS = jobs_df['jobID'].values.tolist()
    for jobID in jobIDS:
        jobIDDict[jobID] = 1

    logger.info('driver(): jobID hashmap created')

    for keyword in searchKeywords:
        logger.info('driver(): attempting to get jobLinks for keyword=%s', keyword)
        getJobLinks("https://au.indeed.com/jobs?q=" + str(keyword))
        logger.info('driver(): sleeping for a random number of time between 100 and 150')
        time.sleep(randint(100,150))

driver()