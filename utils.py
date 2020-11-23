from decouple import config
import csv
import os.path
import gspread

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
