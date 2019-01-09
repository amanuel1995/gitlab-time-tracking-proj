#import the important modules
import requests
import config
import parser as myparser
import jsonresponse as myjson
import math

#################################################################
# endpoints for GitLab API V.4
# issues url 
issues_url = "https://gitlab.matrix.msu.edu/api/v4/issues"

# projects url
proj_url = "https://gitlab.matrix.msu.edu/api/v4/projects"

# users url 
users_url = "https://gitlab.matrix.msu.edu/api/v4/users"

#################################################################
# CONSTANTS used for calculations of total time spent

YEARSECONDS = int(7.513 * math.pow(10, 6))  # according to the U.S. OPM
MONTHSECONDS = 576000   # number of work seconds in a month (40hr * 4 weeks)
WEEKSECONDS = 144000    # number of work seconds in a week (40hr)
DAYSECONDS = 28800      # number of work seconds in a day (8hr)
HOURSECONDS = 3600      # number of seconds in an hr
MINSECONDS = 60         # number of seconds in a min
MAXOBJECTSPERPAGE = 100 # Gitlab Pagination max
#################################################################

# params to inject while sending a GET request
payload = {'per_page': MAXOBJECTSPERPAGE}
#################################################################

def pullProjects():
    """
    Pull all the projects from Matrix Gitlab and return a JSON list of projects
    """
    responseObject = requests.get( proj_url, headers={ "PRIVATE-TOKEN": config.theToken })
    output = responseObject.json()
    
    return output

def projIssue(projID, issueIID):
    """
    Given a project ID, and Issue IID fetch the issue associated with the project

    @param: projID - the ID of the project in the projects list
    @param: issueID - the ID of the specific issue in the project
    @return: issueResponse - a single JSON issue from a single project
    """

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID
    output = requests.get(builtEndPoint, headers={ "PRIVATE-TOKEN": config.theToken })
    issueResponse = output.json()
    
    return issueResponse


def projIssues(projID):
    """
    Given a single project pull all the issues from Gitlab and 
    return a JSON list of issues for the project
    """

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/'
    responseObject = requests.get(builtEndPoint, headers={
                                  "PRIVATE-TOKEN": config.theToken})
    projIssuesList = responseObject.json()
    
    return projIssuesList


def pullUsers():
    """
    Pull the users from Gitlab api an return a JSON object
    
    return: output the JSON response
    """
    
    responseObject = requests.get(users_url, headers={"PRIVATE-TOKEN" : config.theToken})
    userListJson = responseObject.json()
    
    userInfoList = []
    

    for eachObject in userListJson:
        username = eachObject['username']
        userID = eachObject['id']
        name = eachObject['name']

        userInfoList.append([username , name, userID])
    
    return userListJson, userInfoList

def pullNotes(projID, issueIID):
    """
    Get Notes from an issue --> (make this for a specific user)
    param : theURL the endpoint, (maybe theAuthor author of the note, issueIID)
    return: output the JSON response
    """ 
    
    # Given a single ticket, using the gitlab API, read the ticket and all comments on it

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID + '/notes'
    output = requests.get(builtEndPoint, headers={"PRIVATE-TOKEN": config.theToken} , params = payload)
    
    ###########################################################################
    # TODO 
    # pre-process the response output 
    # (issues that have more than 20 per_page / more than a page)
    # get the headers, collect the info X-Total, X-Total-Pages, X-Page, X-Prev-Page, Link
    # 
    # headerDict = output.headers
    # totalItems = headerDict['X-Total']
    # totalPages = headerDict['X-Total-Pages']
    # thisPage = headerDict['X-Page']
    # prevPage = headerDict['X-Prev-Page']
    # nextPage = headerDict['X-Next-Page']      # this returns '' if last page
    # linkContainer = headerDict['Link']        # manipulate this to build endpoints
    ############################################################################

    noteJsonRes = output.json()  

    ####################################################
    # Load the response from external JSON File
    # uncomment the following line and change the jsonresponse.py file 
    #
    # noteJsonRes = myjson.jsonS
    ####################################################
    
    concatNote = ""

    finalDict = {} # has unique usernames as key and {+veTime : x, -veTime: y} as value
    
    # Time info holders
    postiveTime = 0
    negTime = 0
    
    # loop through each note object, extract Author and Comment Body
    for eachNote in noteJsonRes:
        noteBody = eachNote["body"]
        noteAuthor = eachNote["author"]["username"]
        
        # concatenate the note and strip spaces
        concatNote = (noteBody) + ' ' + (noteAuthor)
        concatNote = concatNote.replace(" ", "")
        
        # parse only if note body starts with 'added' or 'subtracted'
        if (noteBody.split(' ')[0] == 'added' or noteBody.split()[0] == 'subtracted'):
            # regex to extract
            result = myparser.parser.parse(concatNote)
        else:
            result = ['', '', '', '', '', '', '', '', '', '']
        
        # make the calculation for every user - per date
        if (result[0] == 'added'):
            # extract the time info from the result list
            year = result[1]
            month = result[2]
            week = result[3]
            day = result[4]
            hr = result[5]
            minutes = result[6]
            
            try:
                # strip the trailing y/mo/h/m info
                year = int(year[:-1]) or 0
            except(ValueError):
                year = 0
            try:
                month = int(month[-2:]) or 0
            except(ValueError):
                month = 0
            try:
                week = int(week[:-1]) or 0
            except(ValueError):
                week = 0
            try:
                day = int(day[:-1]) or 0
            except(ValueError):
                day = 0
            try:
                hr = int(hr[:-1]) or 0
            except(ValueError):
                hr =  0
            try:
                minutes = int(minutes[:-1]) or 0
            except(ValueError):
                minutes = 0
            
            #calcuate
            postiveTime = round((postiveTime + (year*YEARSECONDS) + (month*MONTHSECONDS) + (week*WEEKSECONDS) + (day*DAYSECONDS) + (hr*HOURSECONDS) + (minutes*MINSECONDS))/3600, 2)

        if(result[0] == 'subtracted'):
            # extract the time info from the result list
            year = result[1]
            month = result[2]
            week = result[3]
            day = result[4]
            hr = result[5]
            minutes = result[6]

            # strip the trailing y/mo/h/m info
            try:
                # strip the trailing y/mo/h/m info
                year = int(year[:-1]) or 0
            except(ValueError):
                year = 0
            try:
                month = int(month[-2:]) or 0
            except(ValueError):
                month = 0
            try:
                week = int(week[:-1]) or 0
            except(ValueError):
                week = 0
            try:
                day = int(day[:-1]) or 0
            except(ValueError):
                day = 0
            try:
                hr = int(hr[:-1]) or 0
            except(ValueError):
                hr = 0
            try:
                minutes = int(minutes[:-1]) or 0
            except(ValueError):
                minutes = 0

            #calcuate
            negTime = round((negTime +
                                 (year*YEARSECONDS) + (month*MONTHSECONDS) + (week*WEEKSECONDS) +
                                 (day*DAYSECONDS) + (hr*HOURSECONDS) + (minutes*MINSECONDS))/3600, 2)
        # else: 
        #     pass
        
        dateTimeLogged = result[8]
        
        finalDict.setdefault(dateTimeLogged, []).append(
            {'user': noteAuthor, "positivetime": postiveTime, "negativetime": negTime})
        
        postiveTime, negTime = 0,0 # Reset counters

    return finalDict


def getSingleIssueNote(projID, issueIID, noteID):
    """
    A function to pull a single note for a project issue 
    """

    #build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID + '/notes/' + noteID
    output = requests.get(builtEndPoint, headers={"PRIVATE-TOKEN": config.theToken})
    noteJsonRes = output.json()

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
            if (eachLstItem['user'] not in tmpDict):
                timeDict = {}
                currUserToDict = eachLstItem['user']
                # if the time info is not there, get the info
                timeDict['totPosTime'] = eachLstItem['positivetime']
                timeDict['totNegTime'] = eachLstItem['negativetime']

                # push the dict conataining time info into a temp dict with user as key
                tmpDict[currUserToDict] = timeDict

            elif(eachLstItem['user'] in tmpDict):
                # user to update
                updateUserInDict = eachLstItem['user']
                # if there is an entry for that user, sum the time info as value
                tmpDict[updateUserInDict]['totPosTime'] += eachLstItem['positivetime']
                tmpDict[updateUserInDict]['totNegTime'] += eachLstItem['negativetime']

        timeSpentDictByDate.setdefault(eachDate, []).append(tmpDict)

    # maybe sort the final array based on dates before returning it 
    return timeSpentDictByDate
    

def main():
    """
    The main function
    """
    
    # get list of notes and a few other relevant info
    result = pullNotes("231","3" )
    
    # invoke the function that aggregates time spent info for users summarized to the day
    timeSpentInfo = calculateTimeSpentPerIssue(result)

    print('###################################################################')
    print(timeSpentInfo)
    print('###################################################################')

main()
