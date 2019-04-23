#!/usr/bin/env bash

echo ~~/stor/assets/gitlab-time-summary/jobasset.tgz | mjob create -m 'JOBTIME=`date +%s`; START=`date +%Y-%m-%d -d"sunday 3 weeks ago"`; END=`date +%Y-%m-%d -d"next sunday"`; tar -xzvf $MANTA_INPUT_FILE; python3 apiv0.1.py -d1 $START -d2 $END ; mput -p -f timesheet.csv ~~/stor/reports/gitlab-time-summary/time_summary-$JOBTIME-$START-$END.csv'
