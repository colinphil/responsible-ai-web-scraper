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

# Obtain scraped data from TechCrunch
def scrape(url):
    headers = {
        'User-Agent': str(config('USER_AGENT'))}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    content = soup.findAll('li', {'class': 'ov-a'})
    result = []

    for item in content:
        try:
            newItem = {}
            newItem['Name'] = item.select('a')[0].get('title')
            newItem['Link'] = item.select('a')[0].get('href')
            newItem['Date'] = datetime.datetime.strptime(item.findAll(
                'span', {'class': 'pl-15 bl-1-666'})[0].get_text().replace(',', ''), '%B %d %Y').strftime("%Y/%m/%d")
            if check(newItem['Name']):
                result.append(newItem)
        except Exception as e:
            print('')
    return result

def check(content):
    if (re.compile('AI', re.IGNORECASE).search(content) or re.compile('A.I.', re.IGNORECASE).search(content) 
        or re.compile('artificial intelligence', re.IGNORECASE).search(content) or re.compile('ethics?a?l?', re.IGNORECASE).search(content) 
        or re.compile('biase?s?', re.IGNORECASE).search(content) or re.compile('algorithmi?c?', re.IGNORECASE).search(content) 
        or re.compile('facial recognition', re.IGNORECASE).search(content) or re.compile('rights?', re.IGNORECASE).search(content)
            or re.compile('fears?', re.IGNORECASE).search(content) or re.compile('dangers?', re.IGNORECASE).search(content)):
        return True
    return False

# Convert Data into CSV
def convert(data):
    exists = os.path.isfile('sources.csv')
    columns = ['Name', 'Link', 'Date']
    try:
        with open('sources.csv', 'a') as csvfile:
            writer = csv.DictWriter(
                csvfile, delimiter=',', lineterminator='\n', fieldnames=columns)
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
    # obtain first two results
    result = scrape(
        'https://search.techcrunch.com/search;_ylt=Awr9ImItSrtfWq0AA7ynBWVH;_ylc=X1MDMTE5NzgwMjkxOQRfcgMyBGZyA3RlY2hjcnVuY2gEZ3ByaWQDV1JYVG5TV3JRWHVWXy5tSkNvNzNVQQRuX3JzbHQDMARuX3N1Z2cDMQRvcmlnaW4Dc2VhcmNoLnRlY2hjcnVuY2guY29tBHBvcwMwBHBxc3RyAwRwcXN0cmwDMARxc3RybAM5BHF1ZXJ5A2V0aGljcyUyMGFpBHRfc3RtcAMxNjA2MTA5NzU5?p=ethics+ai&fr2=sb-top&fr=techcrunch')
    sleep(randint(2,10))
    result += scrape('https://search.techcrunch.com/search;_ylt=Awr9JnE_SrtfNYYAUfynBWVH;_ylu=Y29sbwNncTEEcG9zAzEEdnRpZAMEc2VjA3BhZ2luYXRpb24-?p=ethics+ai&fr=techcrunch&fr2=sb-top&b=11&pz=10&bct=0&xargs=0')
    
    # scrape others
    current = 21
    base = 'https://search.techcrunch.com/search;_ylt=Awr9CKpUTrtfRGMAlx2nBWVH;_ylu=Y29sbwNncTEEcG9zAzEEdnRpZAMEc2VjA3BhZ2luYXRpb24-?p=ethics+ai&pz=10&fr=techcrunch&fr2=sb-top&bct=0&b='
    end = '&pz=10&bct=0&xargs=0'

    while current <= 121:
        sleep(randint(2,10))
        result += scrape(base + str(current) + end)
        current += 10

    print(len(result))
    convert(result)
    upload()

if __name__ == "__main__":
    main()
