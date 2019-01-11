#import the important modules
import requests
import config
import parser as myparser
import jsonresponse as myjson
import math
import pytimeparse
import iso8601
import dateutil 

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
#################################################################

# params to inject while sending a GET request
payload = {'per_page': MAXOBJECTSPERPAGE}
#################################################################


def pullUsers():
    """
    Pull the users from Gitlab API and return a JSON list 
    
    """

    responseObject = requests.get(
        users_url, headers={"PRIVATE-TOKEN": config.theToken}, params=payload)
    userListJson = responseObject.json()
    
    # TODO
    # loop over the next pages till the list is exhausted
    # use output.headers dict to extract info neeed to loop

    return userListJson

def pullProjects():
    """
    Pull all the projects from Matrix Gitlab and return a JSON list of projects
    """
    responseObject = requests.get(
        proj_url, headers={"PRIVATE-TOKEN": config.theToken}, params=payload)
    output = responseObject.json()

    # TODO
    # loop over the next pages till the list is exhausted
    # use output.headers dict to extract info neeed to loop

    return output


def pullOneProjIssues(projID):
    """
    Given a single project pull all the issues from Gitlab and 
    return a JSON list of issues for the project
    """

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/'
    responseObject = requests.get(builtEndPoint, headers={
                                  "PRIVATE-TOKEN": config.theToken}, params = payload)
    thisprojIssuesList = responseObject.json()
    
    ###########################################################################
    # TODO
    # pre-process the response output
    # (results that have more than 20 per_page / more than a page)
    # get the headers, collect the info X-Total, X-Total-Pages, X-Page, X-Prev-Page, Link
    #
    # headerDict = responseObject.headers()
    # totalItems = headerDict['X-Total']
    # totalPages = headerDict['X-Total-Pages']
    # thisPage = headerDict['X-Page']
    # prevPage = headerDict['X-Prev-Page']
    # nextPage = headerDict['X-Next-Page']      # this returns '' if last page
    # linkContainer = headerDict['Link']        # manipulate this to build endpoints
    ############################################################################

    # AND refactor the code to a separate function to avoid repetition
    
    return thisprojIssuesList

def pullOneIssue(projID, issueIID):
    """
    Given a project ID, and Issue IID fetch the issue associated with the project

    @param: projID - the ID of the project in the projects list
    @param: issueID - the ID of the specific issue in the project
    @return: issueResponse - a single JSON issue from a single project
    """

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID
    output = requests.get(builtEndPoint, headers={
                          "PRIVATE-TOKEN": config.theToken}, params=payload)
    oneProjIssue= output.json()
    
    # TODO
    # loop over the next pages till the list is exhausted
    # use output.headers dict to extract info neeed to loop

    return oneProjIssue


def pullNotes(projID, issueIID):
    """
    Get Notes from an issue --> (make this for a specific user)
    param : theURL the endpoint, (maybe theAuthor author of the note, issueIID)
    return: output the JSON response
    """

    # Given a single ticket, using the gitlab API, read the ticket and all comments on it

    # build the URL endpoint and extract notes in the issue
    builtEndPoint = proj_url + '/' + projID + '/issues/' + issueIID + '/notes'
    output = requests.get(builtEndPoint, headers={
                          "PRIVATE-TOKEN": config.theToken}, params=payload)
    
    noteJsonRes = output.json()


    ####################################################
    # Load the response from external JSON File
    # uncomment the following line and change the jsonresponse.py file
    #
    # noteJsonRes = myjson.jsonS
    ####################################################
    
    concatNote = ""

    finalDict = {}  # has unique usernames as key and {+veTime : x, -veTime: y} as value

    # Time info holders
    postiveTime = 0
    negTime = 0

    # loop through each note object, extract Author and Comment Body
    for eachNote in noteJsonRes:
        noteBody = eachNote["body"]
        noteAuthor = eachNote["author"]["username"]
        dateTimeLogged = eachNote['']
        # concatenate the note and strip spaces
        concatNote = (noteBody) + ' ' + (noteAuthor)
        #concatNote = concatNote.replace(" ", "")

        dateTimeLogged = 
