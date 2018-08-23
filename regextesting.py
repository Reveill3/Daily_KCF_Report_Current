import re

print(re.findall(r'''
        \d{4}\s[a-zA-z]+\s\d\s
        ([a-zA-Z]+)    
    ''', 'Alerts Report for 1413 Odessa 6 Purple.csv', re.X))
