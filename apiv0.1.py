#!/usr/local/opt/python/bin/

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
    if r.links == {} or r.links['first']['url'] == r.links['last']['url']:
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


def pull_one_proj_issue(projID,issueIID):
    '''
    pull a json object describing a single issue from a specific project
    '''
    endpoint = proj_url + '/' + projID + '/issues/' + issueIID
    issue_json = requests.get(endpoint, headers={"PRIVATE-TOKEN": config.theToken}).json()
    
    # extract the total spent time on the issue by all contributors
    total_time_spent = issue_json['time_stats']['total_time_spent']
    human_total_time_spent = issue_json['time_stats']['human_total_time_spent']

    return issue_json, total_time_spent, human_total_time_spent


def all_issues_for_proj(projID):
    '''
    Pull all the issues within a specific project
    '''
    endpoint = proj_url + '/' + projID + '/issues' + '?sort=asc&order_by=updated_at'
    issues_json = pull_api_response(endpoint)

    return issues_json


def pull_issue_users(projID, issueIID):
    '''
    Pull a collectoin of users who contributd to the specific issue in the proj
    '''

    endpoint =proj_url + projID + '/' +'issues/' + issueIID 
    j_response = pull_api_response(endpoint)
    contributers = j_response['assignees']

    return contributers


def calc_time_from_issue_notes(projID, issueIID):
    """
    Get all the notes from an issue 
    param : theURL the endpoint, issueIID
    return: output the JSON response
    """

    # Given a single ticket, using the gitlab API, read the ticket and all comments on it

    # build the URL endpoint and extract notes in the issue
    built_endpoint = proj_url + '/' + projID + '/issues/' + \
        issueIID + '/notes' + '?sort=asc&order_by=updated_at'

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
        parent_issue = each_note['noteable_iid']

        # check if a time spent information is in the note body else skip
        time_info = 'of time spent at'
        # reset flag - reset all the values to 0 for every author; up to this day
        reset_time_info = 'removed time spent'

        if time_info in note_body:
            # extract username and date
            note_author = each_note["author"]["username"]
            date_time_created = each_note['created_at']

            # concatenate the notebody with username
            concat_notes = (note_body) + ' ' + (note_author)

            # preprocess the date
            dt = dateutil.parser.parse(date_time_created)
            date_time_logged = '%4d-%02d-%02d' % (dt.year, dt.month, dt.day)

            # extract time phrase
            split_at_indx = concat_notes.find(time_info)
            time_phrase = concat_notes[:split_at_indx-1]

            # parse time phrase using the timeparse module and return number of seconds
            total_seconds = pytimeparse.timeparse(time_phrase)

            if (total_seconds >= 0):
                pos_time = total_seconds
            else:
                neg_time = -(total_seconds)

            final_ouput_dict.setdefault(date_time_logged, []).append(
                {'user': note_author, "positivetime": pos_time, "negativetime": neg_time, "issue#": issueIID, "proj#": projID})

        if reset_time_info in note_body:
            # extract who removed time spent info and the date
            note_author = each_note["author"]["username"]
            date_time_created = each_note['created_at']

            # concatenate the notebody with username
            concat_notes = (note_body) + ' ' + (note_author)

            # preprocess the date
            dt = dateutil.parser.parse(date_time_created)
            date_time_logged = '%4d-%02d-%02d' % (dt.year, dt.month, dt.day)

            # reset the time to zero for everyone ... needs more work
            final_ouput_dict = {date_time_logged: [
                {'user': note_author, "positivetime": 0, "negativetime": 0, "issue#": issueIID, "proj#": projID}]}

            # clear_time_spent()
            print('Time info has been cleared on this day: ',
                  date_time_logged, "for issue#", issueIID)

        else:
            pass

        pos_time, neg_time = 0, 0  # Reset counters

    return final_ouput_dict


def calc_time_from_multiple_issues(proj_issues_list):
    '''
    Calculate the time from every issue for a given project
    '''
    extracted_time_info_list = []

    # loop through each issue in that project
    for each_item in proj_issues_list:
        issue_iid = str(each_item['iid'])
        proj_id = str(each_item['project_id'])

        # call the function to extract time info from each note
        issue_notes_time_dict = calc_time_from_issue_notes(proj_id, issue_iid)

        # aggregate time spent for every issue
        time_spent_info_seconds = calculate_time_spent_per_issue(
            issue_notes_time_dict)

        # populate the list
        extracted_time_info_list.append(time_spent_info_seconds)

    return extracted_time_info_list


def calculate_time_spent_per_issue(result_dict):
    """
    Calculate the time spent for a single issue for every user 
    produce a 2D output of date and the corresponding time spent information for each user
    on that date
    """

    # further process the result
    time_spent_dict_per_date = {}

    # final formatting should present dict of {date: {user: [positiveTimeLogged, negativeTimeLogged]}}
    for each_date, each_time_lst in result_dict.items():
        tmp_dict = {}  # intermediate dict
        for each_lst_item in each_time_lst:

            # new user time info for this day
            if (each_lst_item['user'] not in tmp_dict):
                time_dict = {}
                curr_user_to_dict = each_lst_item['user']
                # if the time info is not there, get the info
                time_dict['tot_pos_time'] = each_lst_item['positivetime']
                time_dict['tot_neg_time'] = each_lst_item['negativetime']
                time_dict['issue_id'] = each_lst_item['issue#']
                time_dict["proj_id"] = each_lst_item["proj#"]
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


def calculate_time_spent_per_proj(result_list):
    '''
    Calculate the time spent for a single proj for every user and every issue 
    produce a 2D output of date and the corresponding time spent information for each user for all proj issues
    on that date
    '''
    all_issues_times = []

    for items in result_list:
        time_info_collection = calculate_time_spent_per_issue(items)
        all_issues_times.append(time_info_collection)
    
    return all_issues_times


def ConvertToHumanTime(time_dict):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable (years, months, weeks,days,hours,mins and seconds)
    '''
    humantime_dict_per_date = {}

    for date, user_times in time_dict.items():
        tmp_dict = {}
        for each_user_in_dict in user_times:
            for each_user_key, eachtimeVal in each_user_in_dict.items():
                curr_user = each_user_key
                # grab the total seconds duration
                tot_pos_time = eachtimeVal['tot_pos_time']
                tot_neg_time = eachtimeVal['tot_neg_time']

                # grab the issue# and proj#
                issue_id = eachtimeVal['issue_id']
                proj_id = eachtimeVal['proj_id']

                # convert the seconds to human time (weeks,days,hours,mins and seconds)
                tot_pos_human_time = human_time_delta(tot_pos_time)
                tot_neg_human_time = human_time_delta(tot_neg_time)

                tmp_dict[curr_user] = {
                    'tot_pos_human_time': tot_pos_human_time, 'tot_neg_human_time': tot_neg_human_time, 'issue_id': issue_id, 'proj_id': proj_id}

        humantime_dict_per_date.setdefault(date, []).append(tmp_dict)

    return humantime_dict_per_date


def ConvertToHumanTimeProjIssues(time_lst):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable (years, months, weeks,days,hours,mins and seconds)
    '''
    human_time_lst = []
    for each_obj in time_lst:
        human_time_lst.append(ConvertToHumanTime(each_obj))

    return human_time_lst


def human_time_delta(seconds):
    '''
    convert seconds into human time
    eg. 3600s = 1h 0m
    28860 = 1d 0h 1m 0s 
    144000 = 1w 0d 0h 0m 0s
    '''
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


def net_tot_time_spent_issue(timespent_dict):
    '''
    calculate all the net time spent by all users in a single issue
    '''
    grand_tot_pos = 0
    grand_tot_neg = 0
    for date, user_times in timespent_dict.items():
        for items in user_times:
            for user, times in items.items():
                grand_tot_pos += times['tot_pos_time']
                grand_tot_neg += times['tot_neg_time']

    total_issue_time = grand_tot_pos - grand_tot_neg

    return total_issue_time


def main():
    """
    The main function
    """
    # prompt user for inputs
    proj_id_str = input('Type the project ID or hit enter to skip: ')
    issue_id_str = input('Type the Issue ID or hit enter to skip: ')
    
    print()

    if proj_id_str != '' and issue_id_str =='':
        # user wants all the time info for all issues within the project
        # get list of time info from all the notes in all the issues 
        all_issues_lst = all_issues_for_proj(proj_id_str)
        time_dict = calc_time_from_multiple_issues(all_issues_lst)

        # invoke the function that converts seconds to human time
        # for each issue in project per date per user
        humantime_dict_per_date = ConvertToHumanTimeProjIssues(time_dict)
    
    elif proj_id_str !='' and issue_id_str !='':
        # user wants a list of time info from a specific issue within a project
        # get list of notes and a few other relevant info
        time_dict = calc_time_from_issue_notes(proj_id_str, issue_id_str)

        # invoke the function that aggregates time spent info for users summarized to the day
        time_spent_info_seconds = calculate_time_spent_per_issue(time_dict)

        # invoke the function that converts seconds to human time for each date
        humantime_dict_per_date = ConvertToHumanTime(time_spent_info_seconds)
    else:
        print('INVALID INPUT.')

    print('###################################################################')
    print('Here is the time spent info you requested:-\n')
    print(humantime_dict_per_date)
    print()
    print('###################################################################')

main()