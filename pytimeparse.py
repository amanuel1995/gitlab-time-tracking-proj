#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
timeparse.py
(c) Will Roberts <wildwilhelm@gmail.com>  1 February, 2014
Implements a single function, `timeparse`, which can parse various
kinds of time expressions.
'''

# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

SIGN = r'(?P<sign>(added|subtracted)?\s*?)'
YEARS      = r'(?P<years>\d+)\s*(?:y|yrs?.?|years?)'
MONTHS     = r'(?P<months>\d+)\s*(?:mo|months?)'
WEEKS = r'(?P<weeks>[\d.]+)\s*(?:w|wks?|weeks?)'
DAYS = r'(?P<days>[\d.]+)\s*(?:d|dys?|days?)'
HOURS = r'(?P<hours>[\d.]+)\s*(?:h|hrs?|hours?)'
MINS = r'(?P<mins>[\d.]+)\s*(?:m|mins?|minutes?)'
SECS = r'(?P<secs>[\d.]+)\s*(?:s|secs?|seconds?)'
SEPARATORS = r'[:,\s]'
SECCLOCK = r':(?P<secs>\d{2}(?:\.\d+)?)'
MINCLOCK = r'(?P<mins>\d{1,2}):(?P<secs>\d{2}(?:\.\d+)?)'
HOURCLOCK = r'(?P<hours>\d+):(?P<mins>\d{2}):(?P<secs>\d{2}(?:\.\d+)?)'
DAYCLOCK = (r'(?P<days>\d+):(?P<hours>\d{2}):'
            r'(?P<mins>\d{2}):(?P<secs>\d{2}(?:\.\d+)?)')

def OPT(x): return r'(?:{x})?'.format(x=x, SEPARATORS=SEPARATORS)


def OPTSEP(x): return r'(?:{x}\s*(?:{SEPARATORS}\s*)?)?'.format(
    x=x, SEPARATORS=SEPARATORS)


TIMEFORMATS = [
    r'{YEARS}\s*{MONTHS}\s*{WEEKS}\s*{DAYS}\s*{HOURS}\s*{MINS}\s*{SECS}'.format(
        YEARS=OPTSEP(YEARS),
        MONTHS=OPTSEP(MONTHS),
        WEEKS=OPTSEP(WEEKS),
        DAYS=OPTSEP(DAYS),
        HOURS=OPTSEP(HOURS),
        MINS=OPTSEP(MINS),
        SECS=OPT(SECS)),
    r'{MINS}'.format(
        MINS=OPTSEP(MINS)
    ),
    r'{MINCLOCK}'.format(
        MINCLOCK=MINCLOCK),
    r'{WEEKS}\s*{DAYS}\s*{HOURCLOCK}'.format(
        WEEKS=OPTSEP(WEEKS),
        DAYS=OPTSEP(DAYS),
        HOURCLOCK=HOURCLOCK),
    r'{DAYCLOCK}'.format(
        DAYCLOCK=DAYCLOCK),
    r'{SECCLOCK}'.format(
        SECCLOCK=SECCLOCK),
    r'{YEARS}'.format(
    YEARS=YEARS),
    r'{MONTHS}'.format(
    MONTHS=MONTHS),
]

COMPILED_SIGN = re.compile(r'\s*' + SIGN + r'\s*(?P<unsigned>.*)$')
COMPILED_TIMEFORMATS = [re.compile(r'\s*' + timefmt + r'\s*$', re.I)
                        for timefmt in TIMEFORMATS]

# adapted to work week 
# (8hr/day, 40hr/week, 5days/week, 4 weeks/month and 2,087 hrs/year)
# according to the U.S. OPM average year is 2,087 hrs of work

MULTIPLIERS = dict([
    ('years',   3600 * 2087),
    ('months',  3600 * 160),
    ('weeks',   3600 * 40),
    ('days',    3600 * 8),
    ('hours',   3600),
    ('mins',    60),
    ('secs',    1)
])

def timeparse(sval, granularity='seconds'):
    '''
    Parse a time expression, returning it as a number of seconds.  If
    possible, the return value will be an `int`; if this is not
    possible, the return will be a `float`.  Returns `None` if a time
    expression cannot be parsed from the given string.
    '''
    # Arguments:
    # - `sval`: the string value to parse
    # >>> timeparse('1h 24m')
    # 84
    # >>> timeparse('1 minute, 24 secs')
    # 84
    # >>> timeparse('1m24s')
    # 84
    # Time expressions can be signed.
    # >>> timeparse('- 1m')
    # -60
    # >>> timeparse('+1 minute')
    # 60

    match = COMPILED_SIGN.match(sval)
    sign = -1 if match.groupdict()['sign'] == 'subtracted' else 1
    sval = match.groupdict()['unsigned']
    for timefmt in COMPILED_TIMEFORMATS:
        match = timefmt.match(sval)
        if match and match.group(0).strip():
            mdict = match.groupdict()
            # if all of the fields are integer numbers
            if all(v.isdigit() for v in list(mdict.values()) if v):
                return sign * sum([MULTIPLIERS[k] * int(v, 10) for (k, v) in
                                   list(mdict.items()) if v is not None])
            # if SECS is an integer number
            elif ('secs' not in mdict or
                  mdict['secs'] is None or
                  mdict['secs'].isdigit()):
                # we will return an integer
                return (
                    sign * int(sum([MULTIPLIERS[k] * float(v) for (k, v) in
                                    list(mdict.items()) if k != 'secs' and v is not None])) +
                    (int(mdict['secs'], 10) if mdict['secs'] else 0))
            else:
                # SECS is a float, we will return a float
                return sign * sum([MULTIPLIERS[k] * float(v) for (k, v) in
                                   list(mdict.items()) if v is not None])

# Test the parser

############################################################################
# print(timeparse('2s'))          # 2

# print(timeparse('1m'))          # 60
# print(timeparse('2m 40s'))      # 160

# print(timeparse('1h'))          # 3600
# print(timeparse('2h 20s'))      # 7220
# print(timeparse('2h 2m 30s'))   # 7350

# print(timeparse('1d'))          # 28800
# print(timeparse('10d 2h'))      # 295200
# print(timeparse('1d 25m'))      # 30300
# print(timeparse('2d 20s'))      # 57620
# print(timeparse('1d 50m 5s'))   # 31805
# print(timeparse('1d 30h 20m'))  # 138000  

# print(timeparse('1w'))          # 144000
# print(timeparse('2w 1d'))       # 316800
# print(timeparse('9w 2d 2h'))    # 1360800
# print(timeparse('3w 3d 20h 30m 20s'))   # 516620

# print(timeparse('1mo'))         # 576000
# print(timeparse('10mo 2w'))     # 6048000
# print(timeparse('1mo 2h'))      # 583200
# print(timeparse('1mo 5m'))      # 576300
# print(timeparse('10mo 2w 3d'))  # 6134400
# print(timeparse('1mo 10w 1h 10m'))  # 2020200

# print(timeparse('1y'))          # 7513200
# print(timeparse('1y 2mo'))      # 8665200
# print(timeparse('2y 1mo 2w'))   # 15890400
# print(timeparse('10y 1mo 2w 5h'))           # 76014000
# print(timeparse('1y 10mo 2w 25h 15m'))      # 13652100
# print(timeparse('1y 10mo 2w 25h 15m 30s'))  # 13652130

# test months vs mins

# print(timeparse('1mo'))         # 57600
# print(timeparse('9mo'))         # 5184000
# print(timeparse('10mo'))        # 576000
# print(timeparse('1m'))          # 60
# print(timeparse('9m'))          # 540
# print(timeparse('10m'))         # 600
# print(timeparse('10mins'))      # 600
############################################################################