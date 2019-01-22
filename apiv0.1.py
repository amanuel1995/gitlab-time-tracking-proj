#import the important modules
import requests
import config
import pytimeparse
import dateutil.parser
import json

###### LOAD RESPONSE FROM EXTERNAL JSON FILE ####################
externalJSON = open('testResponse.json').read()
extJSONResponse = json.loads(externalJSON)
#################################################################

#################################################################
# endpoints for GitLab API V.4
# issues url
issues_url = "https://gitlab.matrix.msu.edu/api/v4/issues"

# projects url
proj_url = "https://gitlab.matrix.msu.edu/api/v4/projects"

# users url
users_url = "https://gitlab.matrix.msu.edu/api/v4/users"

#################################################################
# CONSTANTS used
MAXOBJECTSPERPAGE = 100  # Gitlab Pagination max
DEFAULTPERPAGE = 20     # Gitlab default pagination
#################################################################

# params to inject while sending a GET request
payload = {'per_page': DEFAULTPERPAGE}
#################################################################

def pull_api_response(endpoint):
    """
    Loop through the pagination and collect the entire response from API endpoint
    """

    data_set = []

    r = requests.get(endpoint, headers={"PRIVATE-TOKEN": config.theToken}, params=payload)

    raw = r.json()
    for resp in raw:
        data_set.append(resp)

    # handle where the response is only one page
    if r.links['first']['url'] == r.links['last']['url']:
        return data_set
    else:

        while r.links['next']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers={
                            "PRIVATE-TOKEN": config.theToken})
            raw = r.json()
            for items in raw:
                data_set.append(items)

        return data_set

    return data_set

def pullNotes(projID, issueIID):
    """
    Get all the notes from an issue 
    param : theURL the endpoint, issueIID
    return: output the JSON response
    """

    # Given a single ticket, using the gitlab API, read the ticket and all comments on it

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID + '/notes'
    
    noteJsonRes = pull_api_response(builtEndPoint)

    ########### RESPONSE from EXTERNAL JSON File #####################
    # Load the response from external JSON File
    # uncomment the following line and change the jsonresponse.py file
    
    # noteJsonRes = extJSONResponse
    ##################################################################
    
    concatNote = ""

    finalDict = {}  
    # has unique dates as key and list of dicts; usernames as key and {+veTime : x, -veTime: y} as value
    
    # Time info holders
    postiveTime = 0
    negTime = 0

    # loop through each note object, extract Author and Comment Body
    for eachNote in noteJsonRes:
        noteBody = eachNote["body"]

        # check if a time spent information is in the note body else skip
        word = 'of time spent at'

        # reset flag in time spent information
        resetWord = 'removed time spent'
        
        if word in noteBody:  
            # extract username and date
            noteAuthor = eachNote["author"]["username"]
            dateTimeCreated = eachNote['created_at']
            
            # concatenate the note and strip spaces
            concatNote = (noteBody) + ' ' + (noteAuthor)
            
            # preprocess the date
            dt = dateutil.parser.parse(dateTimeCreated)
            dateTimeLogged = '%4d-%02d-%02d' % (dt.year, dt.month, dt.day)

            # extract time phrase
            splitAtIndex  = concatNote.find(word)
            timePhrase = concatNote[:splitAtIndex-1]
            
            # parse time phrase using the timeparse module and return number of seconds
            totalSeconds = pytimeparse.timeparse(timePhrase)

            if (totalSeconds >= 0):
                postiveTime = totalSeconds
            else:
                negTime = totalSeconds

            finalDict.setdefault(dateTimeLogged, []).append(
                {'user': noteAuthor, "positivetime": postiveTime, "negativetime": negTime})

        postiveTime, negTime = 0, 0  # Reset counters

        # elseif we encounter a time spent removed information
        #  reset all the values to 0 for that author 

    return finalDict

def getSingleIssueNote(projID, issueIID, noteID):
    """
    A function to pull a single note for a project, issue 
    """

    #build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + \
        '/issues/' + issueIID + '/notes/' + noteID
    
    noteJsonRes = pull_api_response(builtEndPoint)

    return noteJsonRes

def calculateTimeSpentPerIssue(result):
    """
    Calculate the time spent for a single issue for every user 
    produce a 2D output of date and the corresponding time spent information for each user
    on that date
    """

    # further process the result
    timeSpentDictByDate = {}

    # final formatting should present dict of {date: {user: [positiveTimeLogged, negativeTimeLogged]}}
    for eachDate, eachTimeLst in result.items():
        tmpDict = {}  # intermediate dict
        for eachLstItem in eachTimeLst:
            
            # new user time info for this day
            if (eachLstItem['user'] not in tmpDict):
                timeDict = {}
                currUserToDict = eachLstItem['user']
                # if the time info is not there, get the info
                timeDict['totPosTime'] = eachLstItem['positivetime']
                timeDict['totNegTime'] = eachLstItem['negativetime']

                # push the dict conataining time info into a temp dict with user as key
                tmpDict[currUserToDict] = timeDict
            # add existing user info for this day
            elif(eachLstItem['user'] in tmpDict):
                # user to update
                updateUserInDict = eachLstItem['user']
                # if there is an entry for that user, sum the time info as value
                tmpDict[updateUserInDict]['totPosTime'] += eachLstItem['positivetime']
                tmpDict[updateUserInDict]['totNegTime'] += eachLstItem['negativetime']

        timeSpentDictByDate.setdefault(eachDate, []).append(tmpDict)

    # maybe sort the final array based on dates before returning it
    return timeSpentDictByDate

def ConvertToHumanTime(dict1):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable (years, months, weeks,days,hours,mins and seconds)
    '''
    humanTimeDictPerDate = {}

    for date, userTimes in dict1.items():
        tmpDict = {}
        for eachUserDict in userTimes:
            for eachUserKey, eachtimeVal in eachUserDict.items():
                currUser = eachUserKey
                # grab the total seconds duration
                totPosTime = eachtimeVal['totPosTime']
                totNegTime = eachtimeVal['totNegTime']

                # convert the seconds to human time (weeks,days,hours,mins and seconds)
                totPosHumanTime = human_time_delta(totPosTime)
                totNegHumanTime = human_time_delta(totNegTime)

                tmpDict[currUser] = {
                    'totPosHumanTime': totPosHumanTime, 'totNegHumanTime': totNegHumanTime}

        humanTimeDictPerDate.setdefault(date, []).append(tmpDict)

    return humanTimeDictPerDate

def human_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))

    years, seconds = divmod(seconds, 7513200)
    months, seconds = divmod(seconds, 576000)
    weeks, seconds = divmod(seconds, 144000)

    days, seconds = divmod(seconds, 28800)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if years > 0:
        return '%s%dy %dmo %dw %dd %dh %00dm %00ds' % (sign_string, years, months, weeks, days, hours, minutes, seconds)
    if months > 0:
        return '%s%dmo %dw %dd %dh %00dm %00ds' % (sign_string, months, weeks, days, hours, minutes, seconds)
    if weeks > 0:
        return '%s%dw %dd %dh %00dm %00ds' % (sign_string, weeks, days, hours, minutes, seconds)

    if days > 0:
        return '%s%dd %dh %00dm %00ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh %00dm %00ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%00dm %00ds' % (sign_string, minutes, seconds)
    else:
        return '%s%00ds' % (sign_string, seconds)

def main():
    """
    The main function
    """

    # get list of notes and a few other relevant info
    result = pullNotes("231", "7")

    # invoke the function that aggregates time spent info for users summarized to the day
    timeSpentInfo = calculateTimeSpentPerIssue(result)
    
    # invoke the function that converts seconds to human time for each date
    humanTimeDictPerDate = ConvertToHumanTime(timeSpentInfo)
    
    print('###################################################################')
    print(humanTimeDictPerDate)
    print('###################################################################')

main()
