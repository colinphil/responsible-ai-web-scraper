import gspread

gc = gspread.oauth()
sh = gc.open("Example spreadsheet")
print(sh.sheet.get('A1'))