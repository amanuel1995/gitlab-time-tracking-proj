#import the important modules
import requests
import config
import parser as myparser
import jsonresponse as myjson
from operator import itemgetter

# issues url 
issues_url = "https://gitlab.matrix.msu.edu/api/v4/issues"

# projects url
proj_url = "https://gitlab.matrix.msu.edu/api/v4/projects"

# users url 
users_url = "https://gitlab.matrix.msu.edu/api/v4/users?per_page=100"

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

    # issueResponse = myjson.json
    
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
    # builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID + '/notes'
    # output = requests.get(builtEndPoint, headers={"PRIVATE-TOKEN": config.theToken})
    # noteJsonRes = output.json()  

    noteJsonRes = myjson.jsonS

    concatNote = ""

    # Grab all unique Users who contributed to this issue
    contributorsDict = {}
    tmp_lst = []

    finalDict = {} # has unique usernames as key and {+veTime : x, -veTime: y} as value
    
    for eachNote in noteJsonRes:
        tmp_lst.append(eachNote['author']['username'])

    keys = range(len(tmp_lst))
    values = tmp_lst
    
    for i in keys:
        contributorsDict[i] = values[i]
    
    # Build set of unique contributers for this issue
    uniqueContributers = set(contributorsDict.values())
    
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
            result = ['added', '', '', '', '', '', '']
        
        # make the calculation for every user - per date
        if (result[0] == 'added'):
            # extract the time info from the result list
            day = result[1]
            hr = result[2]
            minutes = result[3]

            try:

                # strip the trailing h/m
                day = day[:-1] or 0
                hr = hr[:-1] or 0
                minutes = minutes[:-1] or 0

                postiveTime = postiveTime + \
                    round(((int(day)*8*3600) + (int(hr) * 3600) + (int(minutes) * 60))/(3600), 3)

            except:
                postiveTime = postiveTime + \
                    round(((int(day)*8*3600) + (int(hr) * 3600) +
                     (int(minutes) * 60))/(3600), 3)

                #print('something wrong has happened while adding/extracting time information.')

        if(result[0] == 'subtracted'):

            # extract the time info from the result list
            #day = result[1]
            hr = result[2]
            minutes = result[3]

            try:
                # strip the trailing h/m
                #day = day[:-1]
                hr = hr[:-1] or 0
                minutes = minutes[:-1] or 0

                #calcuate
                negTime = negTime + \
                    round(((int(day)*8*3600) + (int(hr) * 3600) +
                     (int(minutes) * 60))/(3600), 3)

            except:
                negTime = negTime + \
                    round(((int(day)*8*3600) + (int(hr) * 3600) +
                     (int(minutes) * 60))/(3600), 3)

                #print('something has happened while subtracting/extracting time information.')

            # # Total Sum
            # totalTime = postiveTime - negTime
            
        dateTimeLogged = result[5] or ''
       
        finalDict.setdefault(noteAuthor, []).append({dateTimeLogged: { "positivetime": postiveTime, "negativetime": negTime}})
        
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

def main():
    """
    The main function
    """
    
    # get final data structure for user
    result = pullNotes("231","3" )
    
    #print(result)
    
    # final formatting should present dict of {user: {date: [positiveTimeLogged, negativeTimeLogged]}}
    # for each date sum the the total negative and positive time for every user

    dateDict = {}

    for mainKey, mainValue in result.items():
        for eachValue in mainValue:
            for eachSubKey, Subvalue in eachValue.items():
                dateDict.setdefault(eachSubKey, []).append({'user' : mainKey, 'data' : eachValue[eachSubKey]})
    
    # summarize the postime and negtime for each user for a specific date
    tmpKey = ''
    calcDict = {}
    tmpUser = ''
    for key, value in dateDict.items():
        if tmpKey != key:
            tmpKey = key
            totTimePos =0
            totNegTime =0
            lst = []
            for eachItem in value:
                if( eachItem['user'] != tmpUser ):
                    # add positives , negatives
                    totTimePos += eachItem['data']['positivetime']
                    totNegTime += eachItem['data']['negativetime']
                    tmpUser = eachItem['user']
                    lst.append([tmpUser, totTimePos, totNegTime])
                    calcDict.setdefault(tmpKey, []).append({'info' : lst})
        
        tmpKey = ''

    print(calcDict)
main()
