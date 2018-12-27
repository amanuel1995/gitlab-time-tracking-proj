#import the important modules
import requests
import config
import re
import parsy
import parser as myparser

# issues url 
issues_url = "https://gitlab.matrix.msu.edu/api/v4/issues"

# projects url
proj_url = "https://gitlab.matrix.msu.edu/api/v4/projects"

# users url 
users_url = "https://gitlab.matrix.msu.edu/api/v4/users"


def pullProjects(theURL):
    """
    Pull the projects from Gitlab api an return a JSON object
    param : theURL the endpoint
    return: output the JSON response
    """
    responseObject = requests.get(theURL, headers={"PRIVATE-TOKEN" : config.theToken})
    output = responseObject.json()
    return output


def pullIssues(theURL):
    """
    Pull the issues from Gitlab api an return a JSON object
    param : theURL the endpoint
    return: output the JSON response
    """
    responseObject = requests.get(theURL, headers={"PRIVATE-TOKEN" : config.theToken})
    output = responseObject.json()
    return output


def pullUsers(theURL):
    """
    Pull the users from Gitlab api an return a JSON object
    param : theURL the endpoint
    return: output the JSON response
    """
    responseObject = requests.get(theURL, headers={"PRIVATE-TOKEN" : config.theToken})
    output = responseObject.json()
    return output

def pullNotes(theURL):
    """
    Get Notes from an issue --> (make this for a specific user)
    param : theURL the endpoint, (maybe theAuthor author of the note, issueIID)
    return: output the JSON response
    """ 
    
    # Given a single ticket, using the gitlab API, read the ticket and all comments on it
    
    issuesList = pullIssues(issues_url) # list of all issues by current user
    
    # get the first issue
    issueIID = str(issuesList[0]["iid"]) # hardcoded
    
    # extract the Project ID, Issue ID from each issue 
    projID = "231" # hardcoded

    #build the URL endpoint and extract notes in the issue
    builtEndPoint = theURL + '/' + projID + '/issues/' + issueIID + '/notes'
    output = requests.get(builtEndPoint, headers={"PRIVATE-TOKEN": config.theToken})
    noteResponse = output.json()  
    
    concatNote = ""
    
    # Time calculation/aggregation
    postiveTime = 0
    negTime = 0

    # loop through each note object, extract Date, Author, and Comment Body

    for eachNote in noteResponse:
        noteBody = eachNote["body"]
        noteAuthor = eachNote["author"]["username"]
        noteDate = eachNote["created_at"]
        
        # concatenate the note 
        concatNote = (noteBody) + ' ' + (noteAuthor) 
        
        #strip whitespace from notebody
        concatNote = concatNote.replace(" ", "")
        

        # parse only if it starts with 'added' or 'subtracted'
        if (noteBody.split(' ')[0] == 'added' or noteBody.split()[0] == 'subtracted'):
            # regex to extract
            result = myparser.parser.parse(concatNote)
        else:
            result = ['added', '', '', '', '', '', '']
        
        # loop through each modified note on the issue
        if (result[0] == 'added'):
            
            # extract the time info from the result list
            #day = result[1] 
            hr = result[2] 
            minutes = result[3] 

            try:

                # strip the trailing h/m 
                hr = hr[:-1] or 0
                minutes = minutes[:-1] or 0
                
                postiveTime = postiveTime + ((int(hr) * 3600) + (int(minutes) * 60))
                
            except:
                hr = 0
                minutes = 0
                postiveTime = postiveTime + ((int(hr) * 3600) + (int(minutes) * 60))
                
                print('something wrong has happened while adding/extracting time information.')
        
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
                negTime = negTime + ((int(hr) * 3600) + (int(minutes) * 60))
                
            except:
                hr = 0
                minutes = 0
                negTime = negTime + ((int(hr) * 3600) + (int(minutes) * 60))
                
                print('something has happened while subtracting/extracting time information.')

        # Total Sum 
        totalTime = postiveTime - negTime
        
        print(result)
    
    print('Total Positive Time: ', postiveTime)
    print('Total Negative Time: ', negTime)
    print('Total Time Spent: ',totalTime/3600)

    return result


def calculateTimeFromMatch(match):
    """
    Parse string matches to add/subtract times and return the sum (make this perfor every user)
    param : theMatchObject 
    return: output the Dict {username: [sumTime, dateLogged, dateTimeSpent]}
    """ 
    
#    compList = []
#    count = 0
#    
#    if(match[0] == 'added'):
#        while match[count]:
#            timeData = match[1]
#            compList = timeData.split()
#            1st 
    return 0

def main():
    """
    The main function
    """

    
    # get list of notes and a few other relevant info 
    noteMatches = pullNotes(proj_url)
    
    calculateTimeFromMatch(noteMatches)
    # final formatting should present dict of {date: [author, time_spent, date_logged]}
         
main()
