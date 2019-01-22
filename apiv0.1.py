#import the important modules
import requests
import config
import pytimeparse
import dateutil.parser
import json

###### LOAD RESPONSE FROM EXTERNAL JSON FILE ####################
ext_json_file = open('testResponse.json').read()
external_json_response = json.loads(ext_json_file)
#################################################################

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
DEFAULTPERPAGE = 20     # Gitlab default pagination
#################################################################

# params to inject while sending a GET request
payload = {'per_page': DEFAULTPERPAGE}
#################################################################

def pull_api_response(endpoint):
    """
    Loop through the pages and collect the entire response from API endpoint
    """

    data_set = []

    # send GET request to API endpoint
    r = requests.get(endpoint, headers={"PRIVATE-TOKEN": config.theToken}, params=payload)
    raw = r.json()

    # iterate through each object and append to data_set list
    for resp in raw:
        data_set.append(resp)

    # handle where the response is only one page
    if r.links['first']['url'] == r.links['last']['url']:
        return data_set
    else:
        while r.links['next']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers={
                            "PRIVATE-TOKEN": config.theToken})
            raw = r.json()
            for items in raw:
                data_set.append(items)

        return data_set

    return data_set

def pullNotes(projID, issueIID):
    """
    Get all the notes from an issue 
    param : theURL the endpoint, issueIID
    return: output the JSON response
    """

    # Given a single ticket, using the gitlab API, read the ticket and all comments on it

    # build the URL endpoint and extract notes in the issue
    built_endpoint = proj_url + '/' + projID + '/issues/' + issueIID + '/notes'
    
    notes_json_res = pull_api_response(built_endpoint)

    ########### RESPONSE from EXTERNAL JSON File #####################
    # Load the response from external JSON File
    # uncomment the following line and change the jsonresponse.py file
    
    # notes_json_res = external_json_response
    ##################################################################
    
    concat_notes = ""

    final_ouput_dict = {}  
    # has unique dates as key and list of dicts; usernames as key and {+veTime : x, -veTime: y} as value
    
    # Time info holders
    pos_time = 0
    neg_time = 0

    # loop through each note object, extract Author and Comment Body
    for each_note in notes_json_res:
        note_body = each_note["body"]

        # check if a time spent information is in the note body else skip
        word = 'of time spent at'

        # reset flag in time spent information
        reset_word = 'removed time spent'
        
        if word in note_body:  
            # extract username and date
            note_author = each_note["author"]["username"]
            date_time_created = each_note['created_at']
            
            # concatenate the note and strip spaces
            concat_notes = (note_body) + ' ' + (note_author)
            
            # preprocess the date
            dt = dateutil.parser.parse(date_time_created)
            date_time_logged = '%4d-%02d-%02d' % (dt.year, dt.month, dt.day)

            # extract time phrase
            split_at_indx  = concat_notes.find(word)
            time_phrase = concat_notes[:split_at_indx-1]
            
            # parse time phrase using the timeparse module and return number of seconds
            total_seconds = pytimeparse.timeparse(time_phrase)

            if (total_seconds >= 0):
                pos_time = total_seconds
            else:
                neg_time = total_seconds

            final_ouput_dict.setdefault(date_time_logged, []).append(
                {'user': note_author, "positivetime": pos_time, "negativetime": neg_time})

        pos_time, neg_time = 0, 0  # Reset counters

        # elseif we encounter a time spent removed information
        #  reset all the values to 0 for that author 

    return final_ouput_dict

def getSingleIssueNote(projID, issueIID, noteID):
    """
    A function to pull a single note for a project, issue 
    """

    #build the URL endpoint and extract notes in the issue
    built_endpoint = proj_url + '/' + projID + \
        '/issues/' + issueIID + '/notes/' + noteID
    
    notes_json_res = pull_api_response(built_endpoint)

    return notes_json_res

def calculateTimeSpentPerIssue(result):
    """
    Calculate the time spent for a single issue for every user 
    produce a 2D output of date and the corresponding time spent information for each user
    on that date
    """

    # further process the result
    time_spent_dict_per_date = {}

    # final formatting should present dict of {date: {user: [positiveTimeLogged, negativeTimeLogged]}}
    for each_date, each_time_lst in result.items():
        tmp_dict = {}  # intermediate dict
        for each_lst_item in each_time_lst:
            
            # new user time info for this day
            if (each_lst_item['user'] not in tmp_dict):
                time_dict = {}
                curr_user_to_dict = each_lst_item['user']
                # if the time info is not there, get the info
                time_dict['tot_pos_time'] = each_lst_item['positivetime']
                time_dict['tot_neg_time'] = each_lst_item['negativetime']

                # push the dict conataining time info into a temp dict with user as key
                tmp_dict[curr_user_to_dict] = time_dict
            # add existing user info for this day
            elif(each_lst_item['user'] in tmp_dict):
                # user to update
                updateUserInDict = each_lst_item['user']
                # if there is an entry for that user, sum the time info as value
                tmp_dict[updateUserInDict]['tot_pos_time'] += each_lst_item['positivetime']
                tmp_dict[updateUserInDict]['tot_neg_time'] += each_lst_item['negativetime']

        time_spent_dict_per_date.setdefault(each_date, []).append(tmp_dict)

    # maybe sort the final array based on dates before returning it
    return time_spent_dict_per_date

def ConvertToHumanTime(dict1):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable (years, months, weeks,days,hours,mins and seconds)
    '''
    humantime_dictPerDate = {}

    for date, user_times in dict1.items():
        tmp_dict = {}
        for each_user_in_dict in user_times:
            for each_user_key, eachtimeVal in each_user_in_dict.items():
                curr_user = each_user_key
                # grab the total seconds duration
                tot_pos_time = eachtimeVal['tot_pos_time']
                tot_neg_time = eachtimeVal['tot_neg_time']

                # convert the seconds to human time (weeks,days,hours,mins and seconds)
                tot_pos_human_time = human_time_delta(tot_pos_time)
                tot_neg_human_time = human_time_delta(tot_neg_time)

                tmp_dict[curr_user] = {
                    'tot_pos_human_time': tot_pos_human_time, 'tot_neg_human_time': tot_neg_human_time}

        humantime_dictPerDate.setdefault(date, []).append(tmp_dict)

    return humantime_dictPerDate

def human_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))

    years, seconds = divmod(seconds, 7513200)
    months, seconds = divmod(seconds, 576000)
    weeks, seconds = divmod(seconds, 144000)

    days, seconds = divmod(seconds, 28800)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if years > 0:
        return '%s%dy %dmo %dw %dd %dh %00dm %00ds' % (sign_string, years, months, weeks, days, hours, minutes, seconds)
    if months > 0:
        return '%s%dmo %dw %dd %dh %00dm %00ds' % (sign_string, months, weeks, days, hours, minutes, seconds)
    if weeks > 0:
        return '%s%dw %dd %dh %00dm %00ds' % (sign_string, weeks, days, hours, minutes, seconds)

    if days > 0:
        return '%s%dd %dh %00dm %00ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh %00dm %00ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%00dm %00ds' % (sign_string, minutes, seconds)
    else:
        return '%s%00ds' % (sign_string, seconds)

def main():
    """
    The main function
    """

    # get list of notes and a few other relevant info
    result = pullNotes("239", "1")

    # invoke the function that aggregates time spent info for users summarized to the day
    timeSpentInfo = calculateTimeSpentPerIssue(result)
    
    # invoke the function that converts seconds to human time for each date
    humantime_dictPerDate = ConvertToHumanTime(timeSpentInfo)
    
    print('###################################################################')
    print(humantime_dictPerDate)
    print('###################################################################')

main()
