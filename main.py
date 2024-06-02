import os
import json
import requests
import re
from bs4 import BeautifulSoup

FULL_URL = "https://www.linkedin.com/jobs/search/"
PARAM_GEOID = "90000070"
PARAM_KEYWORDS = "software engineer C++"
PARAM_LOCATION = "New York City Metropolitan Area"

PARAMS = {
    'geoId': PARAM_GEOID,
    'keywords': PARAM_KEYWORDS,
    'location': PARAM_LOCATION,
}

def strain_applicants(soup: BeautifulSoup) -> str:
    """
    Strain the soup for the number of applicants.
    """
    class_options = [
        'num-applicants__caption',
        'tvm__text',
    ]

    for class_name in class_options:
        spans = soup.find_all(
            'span',
            class_=class_name,
        )
        for span in spans:
            t = span.get_text(strip=True)
            m = re.search('(\d+)', t)
            if m:
                return m.group(1)
            
    return 'N/A'

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
DT_PATTERNS = [
    (r'(\d+)\s*minute[s]?\s*ago', 'minutes'),
    (r'(\d+)\s*hour[s]?\s*ago', 'hours'),
    (r'(\d+)\s*day[s]?\s*ago', 'days'),
    (r'(\d+)\s*week[s]?\s*ago', 'weeks'),
    (r'(\d+)\s*month[s]?\s*ago', 'months'),
    (r'(\d+)\s*year[s]?\s*ago', 'years'),
]

def standardize_date(raw_date: str, now: datetime) -> str:
    for pattern, time_unit in DT_PATTERNS:
        m = re.search(pattern, raw_date)
        if m:
            value = int(m.group(1))
            res = None
            if time_unit == 'minutes':
                res = now - timedelta(minutes=value)
            elif time_unit == 'hours':
                res = now - timedelta(hours=value)
            elif time_unit == 'days':
                res = now - timedelta(days=value)
            elif time_unit == 'weeks':
                res = now - timedelta(weeks=value)
            elif time_unit == 'months':
                res = now - timedelta(weeks=value*4)
            elif time_unit == 'years':
                res = now - timedelta(weeks=value*52)

            if res is not None:
                return res.isoformat().split('T')[0]
            
    return 'N/A'

def main():
    r = requests.get(FULL_URL, params=PARAMS)
    print(r.status_code)
    
    if r.status_code != 200:
        return
    
    re_pattern = r'https://www.linkedin.com/jobs/view\S*'
    job_urls = re.findall(re_pattern, r.text)

    job_id_pattern = r'\b\d{10}\b'
    job_ids = set()
    for job_url in job_urls:
        job_id = re.findall(job_id_pattern, job_url)[0]
        job_ids.add(job_id)

    print(f"Found {len(job_ids)} ids")

    # job_ids = set()
    # job_ids.add('3918910604')

    results = []
    now = datetime.now()
    for job_id in job_ids:
        url = f"https://www.linkedin.com/jobs/view/{job_id}"

        print(f"Getting '{url}'...")
        r = requests.get(url)

        # Parse.
        job_soup = BeautifulSoup(r.text, 'html.parser')

        # Get job name.
        job_name_element = job_soup.find(
            'h1',
            class_='top-card-layout__title'
        )

        # Get company name.
        job_company_element = job_soup.find(
            'a',
            class_='topcard__org-name-link topcard__flavor--black-link'
        )

        # Get number of applicants.
        num_applicants = strain_applicants(job_soup)

        # Get post time.
        job_posttime_element = job_soup.find(
            'span',
            class_='posted-time-ago__text topcard__flavor--metadata'
        )

        # Get salary range.
        job_salary_pattern = r'\S+/yr'
        job_salary_matches = re.findall(job_salary_pattern, r.text)
        job_salary = "N/A"
        if len(job_salary_matches) > 0:
            job_salary = ' - '.join(job_salary_matches)

        data = {}

        data['job_name'] = 'N/A' if job_name_element is None else job_name_element.text.strip()
        data['company_name'] = 'N/A' if job_company_element is None else job_company_element.text.strip()
        data['num_applicants'] = num_applicants
        data['post_time'] = 'N/A' if job_posttime_element is None else job_posttime_element.text.strip()
        data['std_post_time'] = standardize_date(data['post_time'], now)
        data['url'] = url
        data['salary_range'] = job_salary

        results.append(data)
        break

    with open('data.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__=='__main__':

    main()
