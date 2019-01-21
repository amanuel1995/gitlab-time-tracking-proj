### Matrix Works API - BluePrint

### Issue 1

* Compare net time spent for a single issue with total_human_time_spent for the issue
* Loop through the API response to fetch all the result till EOL
* Handle string simulation of API response (''added ..., subtracted...")
* Handle "Removed Time Spent" cases for each user
* Handle Edge cases (too huge time info, too little)



```python
def calculateTotalTimePerIssue(aggregatedDict) {
    
    allUserNetTimeSpent = 0
    allUserPosTime = 0
    allUserNegTime = 0
    total_human_time_spent = pullOneiIssue(projID, issueIID)['time_stats']['human_total_time_spent']
    total_time_spent = pullOneiIssue(projID, issueIID)['time_stats']['total_time_spent']
    for eachDate, userTimes in aggregatedDict.iteritems():
    	for eachUserTime in userTimes:
    		# TODO
    		# Add the total positive
    		# Add the total negative
    		# get the net time spent
    # compare all time spent for all users across all days 
    # with total_human_time_spent for that issue
    # call second to human time converter on total_human_time_spent
    # or use total_time_spent instead and compare the seconds
}
```

_Compare net time spent for a single issue with total_human_time_spent for the issue_



```python
def resetTimeLogged(author, date, timeSpentDict) {
    '''Reset the summed time to zero for that author for all the days before date'''
   
    # find the author in the timeSpentDict, handle error if not there
    # for all the days before 'date'
        # Reset both positive and negative time for that author
    return modifiedDict
    
}
```

_Handle "Removed Time Spent" cases for each user_