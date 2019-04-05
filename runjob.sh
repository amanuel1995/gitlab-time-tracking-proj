#!/usr/bin/env bash

echo ~~/stor/assets/gitlab-time-summary/jobasset.tgz | mjob create -m 'tar -xzvf $MANTA_INPUT_FILE; python3 apiv0.1.py -d1 `date +%Y-%m-%d -d"3 weeks ago"` -d2 `date +%Y-%m-%d `; mput -p -f timesheet.csv ~~/stor/reports/gitlab-time-summary/timesheet-`date +%Y-%m-%d `.csv'
