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


def getJobLinks(page):

    baseURL = "https://au.indeed.com"
    logger.debug('getJobLinks() called page=%s, baseURL=%s', page, baseURL)
    logger.debug('attempting to download source for %s', page)
    source = requests.get(page).text
    soup = BeautifulSoup(source, 'html.parser')

    if soup:
        logger.debug('successfully downloaded %s', page)
    else:
        logger.error('unsuccessful attempt at downloading %s', page)
        exit()

    numberOfJobs = extractNumberOfJobs(soup)
    if numberOfJobs:
        logger.debug('located a total number of %s jobs', numberOfJobs)
    else:
        logger.error('unable to determine number of jobs')


    jobsPerPage = 0
    cleanJobs = []

    while jobsPerPage < numberOfJobs:

        logger.debug('scraping job links for batch %s of %s', jobsPerPage, numberOfJobs)

        url = page + '&start=' + str(jobsPerPage)

        logger.debug('-- attempting to download for %s', url)
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'html.parser')

        jobLinks = soup.find_all('a', attrs={'class': 'jobtitle'})
        logger.info('-- found %s jobs on the page', len(jobLinks))

        if jobLinks:
            for link in jobLinks:
                #TODO:  Handle Advertisements better

                if '/pagead/' in link['href']:
                    logger.info('-- found page advertisement, skipping these for now now')
                else:
                    cleanString = str(baseURL) + link['href']
                    logger.info('-- found jobID=%s', extractJobID(cleanString))
                    cleanJobs.append(cleanString)
                    getJobInformation(cleanString)

        else:
            logger.info('unable to extract jobs')

        logger.info('-- sleeping for 0.5s')

        time.sleep(0.5)
        jobLinks = []
        jobsPerPage += 10 

    logger.info('OPS:  Found %s jobs', len(cleanJobs))



    return cleanJobs

def getJobInformation(url):

    if "/pagead/" in url:
        pass
    else:
        logger.debug('getJobInformation() called for url=%s', url)

        jobID = extractJobID(url)

        if str(jobID) in jobIDDict:
            logger.info('Already found this before - SKIPPING %s', jobID)
            return 
        else:
            logger.info('%s is a new job according to hashmap', jobID)
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
                'metaScrapeURL': '-' #TODO:  Capture what the scrape URL and parameters were
            }
            
            df = pd.DataFrame(DataDict, index=[0])
            print(df)
            df.to_csv('jobs.csv', mode='a', header=False)
            logger.debug('appended data to jobs.csv')
            return df 


def driver():
    logger.info('driver executed')

    # searchKeywords = ['cyber+security', 'information+security', 'cybersecurity', 'infosec', 'security', 'security+consultant', 'security+engineer', 'risk+management', 'grc']

    searchKeywords = ['security+engineer']

    logger.info('preparing the dictionary hashmap')
    # Preparing dictionary for hashmap
    jobs_df = pd.read_csv('./jobs.csv', names=['index', 'jobID', 'jobTitle', 'jobCompanyName', 'jobLocation', 'jobPeriod', 'jobSalary', 'jobDescription', 'jobPostDate', 'jobExternalLink', 'metaScrapeDatetime'])
    global jobIDDict
    jobIDDict = {}
    jobIDS = jobs_df['jobID'].values.tolist()
    
    for jobID in jobIDS:
        jobIDDict[jobID] = 1


    logger.info('successfully finished the dictionary hashmap')
    for keyword in searchKeywords:
        logger.info('attempting to get jobLinks for keyword=%s', keyword)
        getJobLinks("https://au.indeed.com/jobs?q=" + str(keyword))
        logger.info('sleeping for 10s')
        time.sleep(10)

driver()