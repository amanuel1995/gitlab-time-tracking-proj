#import the important modules
import requests
import json
import config
import re

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
    oneIssue = issuesList[0]
    
    # parse the ticket and read all comments on it
    # extract the Project ID, Issue ID from each issue 
    projID = "239"#str(oneIssue["projID"])
    issueIID = str(oneIssue["iid"])

    #build the URL endpoint and extract 
    builtEndPoint = theURL + '/' + projID + '/issues/' + issueIID + '/notes'
    output = requests.get(builtEndPoint, headers={"PRIVATE-TOKEN": config.theToken})
    noteResponse = output.json()  
    
    concatNote = ""
    myDict = {}
    
    # loop through each note object, extract Date, Author,  and Comment Body
    for eachNote in noteResponse:
        noteBody = eachNote["body"]
        noteAuthor = eachNote["author"]["username"]
        Date = eachNote["created_at"]
        
        # concatenate the note 
        concatNote = (noteBody) + " " + (noteAuthor) + " "+ (Date)
        
        # regex to extract (d+(mo)\s\d+(w)\s\d+(d)) #### parse the JSON instead? ####
        pattern = re.compile(r'^(?:added\s|subtracted\s)(\d+(mo)\s)?(\d+(w)\s)?'+ 
                             '(\d+(d)\s)?(\d+(h)\s)?(\d+(m)\s)?of\stime\sspent\\'+
                             'sat\s\d+-\d+-\d+\s\w+[.]\w+\s\d+-\d+-\d+(T)\d+[:]\d+[:]\d+[.]\d+[Z]$')
        matches = pattern.finditer(concatNote)
        
        #matchesTuple = matches(matches)
        
        #populate the dictionary based on key = date, and value (string of author, body)
        myDict[Date] = concatNote
        
        
        ctr, mylist = 1, []
        
        for match in matches:
            timeInfo = match.group(0).split(" ")
            if (timeInfo[0] == 'added'):
                while(timeInfo[ctr] != 'of'):
                    mylist.append(timeInfo[ctr])
                    ctr +=1
            print(timeInfo)
            
    return matches
    

#def parseJSONNote():
#    """
#    Parse JSON Notes from an issue --> (make this for a specific user)
#    param : theURL the endpoint, 
#    return: output the JSON response
#    """ 


#def calculateTimeFromMatch():
#    """
#    Parse string matches to add/subtract times and return the sum (make this perfor every user)
#    param : theMacthObject 
#    return: output the Dict {username: [sumTime, dateLogged, dateTimeSpent]}
#    """ 



def main():
    """
    The main function
    """

    
    # get list of notes and a few other relevant info 
    notes = pullNotes(proj_url)


    # final formatting should present dict of {date: [author, time_spent, date_logged]}
         
main()