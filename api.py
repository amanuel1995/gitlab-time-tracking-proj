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

def pullNotes(theURL, projID, issueID):
    """
    Get Notes from an issue
    param : theURL the endpoint, projID the project ID, issueID the issue ID
    return: output the JSON response
    """
    rebuiltEndPoint = theURL + '/' + projID + '/issues/' + issueID + '/notes'
    responseObject = requests.get(rebuiltEndPoint, headers={"PRIVATE-TOKEN": theToken})
    output = responseObject.json()
    return output

def main():
    """
    The main function
    """

    # Given a single ticket, using the gitlab API, read the ticket and all comments on it
    issuesList = pullIssues(issues_url)

    # parse the ticket and read all comments on it

    for item in issuesList:
       
        thisProjectID = str(item["project_id"])
        thisIssueID = str(item["id"])

        noteOutput = pullNotes(proj_url, thisProjectID, thisIssueID)
        
        print("------------------------------------------------------")
        
        print(noteOutput)
     
#main()