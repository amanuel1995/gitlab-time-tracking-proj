from parsy import string, regex, seq

otherNotes = regex('([a-z]+ [a-z]+? [a-z]+?)?').desc('all other irrelavant notes')

addsub = regex('added|subtracted').desc('subtract or add ')
year = regex('([0-9]{0,}y)?').desc('year in [0-9]y format')
month = regex('([0-9]{0,}mo)?').desc('Month in [0-9]mo format')
week = regex('([0-9]{0,}w)?').desc('Week in [0-9]w format')
day = regex('([0-9]{0,}d)?').desc('Day in [0-9]d format')
hrs = regex('([0-9]{0,}h)?').desc('hrs in [0-9]h format')
mins = regex('([0-9]{0,}m)?').desc('mins in [0-9]m format')
user = regex('([a-z]{1,}.[a-z]{1,})?').desc('User in [a-z]{1,}.[a-z]{1,} format')
time_spentstr = regex('(([a-z]+){4})?').desc('of time spent at ')
date = regex('([0-9]{4}-[0-9]{2}-[0-9]{2})?').desc('Date in yyyy-mm-dd format')

parser = seq( addsub, year, month, week, day, hrs, mins, time_spentstr, date, user)

#############################################################
# the result from the parser will be a list with these values
# index                     # value
#   0                       added/subtracted
#   1                       year
#   2                       month
#   3                       week
#   4                       day
#   5                       hours
#   6                       mins
#   7                       "of time spent at"
#   8                       "YYY-MM-DD"
#   9                       "user.name"  
#############################################################