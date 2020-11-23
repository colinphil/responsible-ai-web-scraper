from bs4 import BeautifulSoup
from decouple import config
from time import sleep
from random import randint
import requests
import datetime
import csv
import os.path
import gspread
import re

# Obtain scraped data from Google Scholar
def scrape(url):
    headers = {
        'User-Agent': str(config('USER_AGENT'))}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    content = soup.select('[data-lid]')
    print(content)
    result = []
 
    for item in content:
        try:
            newItem = {}
            newItem['Name'] = item.select('h3')[0].get_text().replace('[HTML]', '').strip()
            newItem['Name'] = newItem['Name'].replace('[PDF]', '').strip()
            newItem['Link'] = item.select('a')[0].get('href')
            newItem['Date'] = (datetime.date.today() - datetime.timedelta(int(item.findAll('div', {"class": "gs_rs"})[0].select('span')[0].get_text().split(' ')[0]))).strftime("%Y/%m/%d")
            if check(newItem['Name']):
                result.append(newItem) 
        except Exception as e:
            print('')
    return result

def check(content):
    if re.compile('AI', re.IGNORECASE).search(content) or re.compile('A.I.', re.IGNORECASE).search(content) or re.compile('artificial intelligence', re.IGNORECASE).search(content):
        return True
    return False

# Convert Data into CSV
def convert(data):
    exists = os.path.isfile('sources.csv')
    columns = ['Name', 'Link', 'Date']
    try:
        with open('sources.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=columns)
            if not exists:
                writer.writeheader()
            for record in data:
                writer.writerow(record)
    except IOError:
        print('I/O Error')

# Upload CSV to Google Drive
def upload():
    gc = gspread.oauth()
    sh = gc.open_by_key(str(config('FILE_KEY')))

    with open('sources.csv', 'r') as file_obj:
        content = file_obj.read().encode('utf-8')
        gc.import_csv(sh.id, data=content)

def main():
    result = scrape(
        'https://scholar.google.com/scholar?hl=en&as_sdt=0,6&q=%22responsible+ai%22&scisbd=1')
    sleep(randint(2,10))
    result += scrape(
        'https://scholar.google.com/scholar?hl=en&as_sdt=0,6&q=harmful+ai&scisbd=1'
    )
    sleep(randint(2, 10))
    result += scrape(
        'https://scholar.google.com/scholar?hl=en&as_sdt=0,6&q=ethics+ai&scisbd=1'
    )
    convert(result)
    upload()

if __name__ == "__main__":
    main()
