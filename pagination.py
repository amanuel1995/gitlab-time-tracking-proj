import config
import re
import requests

issues_url = "https://gitlab.matrix.msu.edu/api/v4/issues"

# projects url
proj_url = "https://gitlab.matrix.msu.edu/api/v4/projects"

# users url
users_url = "https://gitlab.matrix.msu.edu/api/v4/users"



def pullOneProjIssues(projID):
    """
    Given a single project pull all the issues from Gitlab and 
    return a JSON list of issues for the project
    """

    # call the function to send request to API endpoint 
    endpoint = 'https://gitlab.matrix.msu.edu/api/v4/projects/239/issues/1/notes'
    thisProjectIssues = fetchAPIresponse(endpoint)
     
    return thisProjectIssues


def fetchAPIresponse(endPoint):
    '''
    Handle Paginated response
    '''
    # send a GET request to the API endpoint
    initAPIresponse = requests.get(endPoint, headers={"PRIVATE-TOKEN": config.theToken})

    #####################################################################################
    # extract information from API response headers
    # (results that have more than 20 per_page / more than a page)
    # get the headers, collect the info X-Total, X-Total-Pages, X-Page, X-Prev-Page, Link
    #####################################################################################

    headerDict = initAPIresponse.headers
    nextPage = headerDict['X-Next-Page']
    linkContainer = headerDict['Link']

    final_api_res = [initAPIresponse]

    while nextPage != '':
        # extract the link header to get the references to next page
        paginated_urls = generate_endpoints(linkContainer)

        # collect endpoints
        next_endpoint = paginated_urls['next']

        nextAPIresponse = requests.get(next_endpoint, headers={"PRIVATE-TOKEN": config.theToken})
        # update what next page points to
        nextPage = nextAPIresponse.headers['X-Next-Page'] # fetch the new next page
        linkContainer = nextAPIresponse.headers['Link'] # fetch the new link headers

        final_api_res.append(nextAPIresponse)
        nextAPIresponse = '' # reset 
    
    return final_api_res


def generate_endpoints(linkContainer):
    
    # manipulate the endpoint returned
    LinksList = linkContainer.split(',')

    link_list = []
    rel_list = []

    for items in LinksList:
        try:
            links_match = re.search('<(.*)>', items)
            rel_match = re.search('rel="(.*)"', items)

            link_list.append(links_match.group(1))  # list of urls
            rel_list.append(rel_match.group(1))  # list of what the urls are
        except:
            pass

    # zip the two lists
    zippedDict = dict(zip(rel_list, link_list))

    return zippedDict
