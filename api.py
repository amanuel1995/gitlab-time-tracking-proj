#import the important modules
import requests
import config
import re
import parser

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
    issueIID = str(issuesList[0]["iid"])
    
    # extract the Project ID, Issue ID from each issue 
    projID = "231" #str(oneIssue["projID"])

    #build the URL endpoint and extract notes in the issue
    builtEndPoint = theURL + '/' + projID + '/issues/' + issueIID + '/notes'
    output = requests.get(builtEndPoint, headers={"PRIVATE-TOKEN": config.theToken})
    noteResponse = output.json()  
    
    concatNote = ""
    #myDict = {}
    
    # loop through each note object, extract Date, Author,  and Comment Body

    for eachNote in noteResponse:
        noteBody = eachNote["body"]
        noteAuthor = eachNote["author"]["username"]
        Date = eachNote["created_at"]
        
        # concatenate the note 
        concatNote = (noteBody) + " " + (noteAuthor)
        
        # regex to extract (d+(mo)\s\d+(w)\s\d+(d)) #### parse the JSON instead? ####
        pattern = re.compile(r'^(?:(added|subtracted)\s((\d+\w+\s)+)of\stime\sspent\sat\s)(\d+-\d+-\d+)\s(\w+.\w+)')
        matches = pattern.findall(concatNote)
                
        #populate the dictionary based on key = date, and value (string of author, body)
        #myDict[Date] = concatNote
        
        
#        print(concatNote)
#        ctr, mylist = 1, []
#        
#        for match in matches:
#            timeInfo = match.group(0).split(" ")
#            if (timeInfo[0] == 'added'):
#                while(timeInfo[ctr] != 'of'):
#                    mylist.append(timeInfo[ctr])
#                    ctr +=1
#                x = 0
#                while (x < len(mylist)):
#                    print(mylist[x])
#                    x +=1
#            print(timeInfo)
        
        totalTime = 0
        subTime = 0
        
        for match in matches:
            if (match[0] == 'added'):
                
                splittedTime = match[1].split()
                
                try:
                    hr = splittedTime[0][:-1]
                    mins = splittedTime[1][:-1]
                    
                    totalTime += ((int(hr) * 3600) + (int(mins) * 60))
                    
                except:
                    hr = 0
                    
                    mins = splittedTime[0][:-1]
                    totalTime +=  (int(mins) * 60)
            
            if(match[0] == 'subtracted'):
                
                splittedTime = match[1].split()
                try:
                    hr = splittedTime[0][:-1]
                    mins = splittedTime[1][:-1]
                    
                    print("hr: ", hr , "mins: ", mins)
                    
                    subTime += ((int(hr) * 3600) + (int(mins) * 60))
                    
                except:
                    hr = 0
                    mins = splittedTime[0][:-1]
                    
                    print("hr: ", hr , "mins: ", mins)
                     
                    subTime += ((int(mins) * 60))
            print(subTime)
            totalTime = totalTime - subTime
            
            print(match)
            
    print(totalTime/3600)

        
    return matches
    


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