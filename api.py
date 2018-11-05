#import the important modules
import requests
import json
import config

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
    Get Notes from an issue
    param : theURL the endpoint, projID the project ID, issueIID the issue ID
    return: output the JSON response
    """ 
    
    # Given a single ticket, using the gitlab API, read the ticket and all comments on it
    
    issuesList = pullIssues(issues_url) # list of all issues by current user
    
    # get the first issue
    oneIssue = issuesList[0]
    
    # parse the ticket and read all comments on it
    # extract the Project ID, Issue ID from each issue 
    projID = str(oneIssue["project_id"])
    issueIID = str(oneIssue["iid"])

    #build the URL endpoint and extract 
    rebuiltEndPoint = theURL + '/' + projID + '/issues/' + issueIID + '/notes'
    output = requests.get(rebuiltEndPoint, headers={"PRIVATE-TOKEN": config.theToken})
    noteResponse = output.json()  
    
    listIssueNotes = []
    concatNote = ""
    myDict = {}
    
    # loop through each note object, extract Date, Author,  and Comment Body
    for eachNote in noteResponse:
        noteBody = eachNote["body"]
        noteAuthor = eachNote["author"]["name"]
        Date = eachNote["created_at"]
        #timeSpent = 
        
        concatNote = (noteBody) + " " + (noteAuthor) + " "+ (Date)
        listIssueNotes.append(concatNote)
        
        myDict[Date] = concatNote
        # maybe make a dict of {issue: List of issue notes}
        
    return myDict
    

def main():
    """
    The main function
    """
    
    print("Note-Body\t\t Author\t\t Date\t")
    # get list of notes and a few other relevant info 
    notes = pullNotes(proj_url)
    
    for k,v in notes.items():
        print(k,v)
    # final formatting should present dict of {date: [author, time_spent, date_logged]}
         
main()