from bs4 import BeautifulSoup
from decouple import config
import requests
import datetime
import csv
import os.path
import gspread

# Obtain scraped data from Google Scholar
def scrape(url):
    headers = {
        'User-Agent': str(config('USER_AGENT'))}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    content = soup.select('[data-lid]')
    result = []
    print(content)

    for item in content:
        try:
            newItem = {}
            newItem['Name'] = item.select('h3')[0].get_text().replace('[HTML]', '').strip()
            newItem['Link'] = item.select('a')[0].get('href')
            # newItem['Date'] = (datetime.date.today() - datetime.timedelta(int(item.findAll('div', {"class": "gs_rs"})[0].select('span')[0].get_text().split(' ')[0]))).strftime("%Y/%m/%d")
            result.append(newItem)
        except Exception as e:
            print('')
    return result

# Convert Data into CSV
def convert(data):
    exists = os.path.isfile('gscholar.csv')
    columns = ['Name', 'Link', 'Date']
    try:
        with open('gscholar.csv', 'a') as csvfile:
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

    with open('gscholar.csv', 'r') as file_obj:
        content = file_obj.read().encode('utf-8')
        gc.import_csv(sh.id, data=content)

def main():
    responsibleData = scrape(
        'https://scholar.google.com/scholar?hl=en&as_sdt=0,6&q=responsible+ai')
    harmfulData = scrape(
        'https://scholar.google.com/scholar?hl=en&as_sdt=0,6&q=harmful+ai'
    )
    ethicalData = scrape(
        'https://scholar.google.com/scholar?hl=en&as_sdt=0,6&q=ethics+ai&scisbd=1'
    )
    convert(responsibleData + harmfulData + ethicalData)
    upload()

if __name__ == "__main__":
    main()
