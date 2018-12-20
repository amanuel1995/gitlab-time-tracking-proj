from parsy import string, regex

addsub = regex('added|subtracted').desc('subtract or add ')
month = regex('([0-9]{0,2})mo').desc('Month in [0-9]mo format')
week = regex('([0-9]{0,2})w').desc('Week in [0-9]w format')
day = regex('([0-9]{0,2})d').desc('Day in [0-9]d format')
hrs = regex('[0-9]{0,2}h').desc('hrs in [0-9]+h format')
mins = regex('[0-9]{0,}m').desc('mins in [0-9]+m format')
user = regex('[a-z]{1,}.[a-z]{1,}').desc('User in [a-z]+.[a-z]+ format')
date = regex('[0-9]{4}-[0-9]{2}-[0-9]{2}').desc('Date in yyyy-mm-dd format')

parser = addsub + hrs + mins 

parser.parse('added45m')

