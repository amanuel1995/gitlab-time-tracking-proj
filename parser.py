from parsy import string, regex

addsub = regex('added|subtracted').map(string).desc('subtract or add')
month = regex('([0-9]{0,2} )?').desc('Month in [0-9]mo format')
week = regex('([0-9]{0,2} )?').desc('Week in [0-9]w format')
day = regex('([0=9]{0,31} )?').desc('Day in [0-9]d format')
hrs = regex('[0-9]{0,2} ').desc('hrs in [0-9]+h format')
mins = regex('[0-9]+ ').desc('mins in [0-9]+m format')
user = regex('[a-z]+[.][a-z]+ ').desc('User in [a-z]+.[a-z]+ format')
date = regex('[0-9]{4}-[0-9]{2}-[0-9]{2} ').desc('Date in yyyy-mm-dd format')

parser = addsub+month+week+day+hrs+mins+date+user

parser.parse_partial('added 4hr 45m 2018-01-02 amanuel.goshu')
