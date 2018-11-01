#import the important modules
import requests
import json

# GitLab api token
theToken = "2xywL1bzgihh5iq4npox"

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
    responseObject = requests.get(theURL, headers={"PRIVATE-TOKEN" : theToken})
    output = responseObject.json()
    return output


def pullIssues(theURL):
    """
    Pull the issues from Gitlab api an return a JSON object
    param : theURL the endpoint
    return: output the JSON response
    """
    responseObject = requests.get(theURL, headers={"PRIVATE-TOKEN" : theToken})
    output = responseObject.json()
    return output


def pullUsers(theURL):
    """
    Pull the users from Gitlab api an return a JSON object
    param : theURL the endpoint
    return: output the JSON response
    """
    responseObject = requests.get(theURL, headers={"PRIVATE-TOKEN" : theToken})
    output = responseObject.json()
    return output

def pullNotes(theURL):
    """
    Get Notes from an issue
    param : theURL the endpoint, projID the project ID, issueIID the issue ID
    return: output the JSON response
    """ 
    subList = []
    llist = []
    
    # Given a single ticket, using the gitlab API, read the ticket and all comments on it
    issuesList = pullIssues(issues_url)

    # parse the ticket and read all comments on it
    for eachIssue in issuesList:
        # extract the Project ID, Issue ID from each issue 
        projID = str(eachIssue["project_id"])
        issueIID = str(eachIssue["iid"])

        #build the URL endpoint and extract 
        rebuiltEndPoint = theURL + '/' + projID + '/issues/' + issueIID + '/notes'
        output = requests.get(rebuiltEndPoint, headers={"PRIVATE-TOKEN": theToken})
        noteObject = output.json()  
        
        #Maybe move the following loop to main and the two lists as well
   
        # loop through each note object, extract Date, Author,  and Comment Body
        for eachNotes in noteObject:
            noteBody = eachNotes["body"]
            noteAuthor = eachNotes["author"]["name"]
            Date = eachNotes["created_at"]
            
            subList.append(noteBody)
            subList.append(noteAuthor)
            subList.append(Date)
            
            # no info as to which notes belong to which issue
            # maybe make a dict of {issue: List of issue notes}
            
    llist.append(subList) 
    return llist
    

def main():
    """
    The main function
    """
    
    # get list of notes and a few other relevant info 
    notes = pullNotes(proj_url)
    
    for items in notes:
        for item in items:
            print(item)
        
    # final formatting should present dict of {date: [author, time logged]}
    
           
main()