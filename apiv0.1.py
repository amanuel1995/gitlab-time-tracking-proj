# set interpreter and encoding
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import the important modules
import requests
import config
import pytimeparse
import dateutil.parser
import json
import re
import csv
import pandas

###### LOAD RESPONSE FROM EXTERNAL JSON FILE ####################
# ext_json_file = open('testResponse.json').read()
# external_json_response = json.loads(ext_json_file)
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
DEFAULTPERPAGE = 20     # Preferred items per page number
#################################################################

# params to inject while sending a GET request
payload = {'per_page': MAXOBJECTSPERPAGE}
#################################################################


def pull_api_response(endpoint):
    """
    Loop through the pages and collect the entire response from API endpoint
    return a list object containing api response
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
    # handle pagination where the response is multiple page
    else:
        while r.links['next']['url'] != r.links['last']['url']:
            r = requests.get(r.links['next']['url'], headers={"PRIVATE-TOKEN": config.theToken})
            raw = r.json()
            for items in raw:
                data_set.append(items)
    # grab the last page and append it
    if r.links['next']['url'] == r.links['last']['url']:
        r = requests.get(r.links['next']['url'], headers={"PRIVATE-TOKEN": config.theToken})
        raw = r.json()
        for records in raw:
            data_set.append(records)

    return data_set


def pull_all_issues_for_a_proj(projID):
    '''
    Pull all the issues within a specific project
    return issues_json (the list containing all issues for that project)
    '''
    endpoint = proj_url + '/' + projID + '/issues'
    issues_json = pull_api_response(endpoint)

    return issues_json


def pull_issue_users(projID, issueIID):
    '''
    Pull a collection of users who contributed to the specific issue in the proj
    return contributers list of assignees
    '''

    endpoint = proj_url + projID + '/' +'issues/' + issueIID 
    j_response = pull_api_response(endpoint)
    contributers = j_response[0]['assignees'] # this actually is not the right way.

    return contributers


def pull_all_project_all_issues():
    '''
    Pull all projects list from the matrix gitlab
    return list of all the projects
    '''

    endpoint = proj_url + '/?sort=asc'
    all_projs = pull_api_response(endpoint)

    grand_list = []

    # for each the project object in all_projs api response invoke the function to extract issues
    for each_project in all_projs:
        project_id = str(each_project["id"])
        
        # pull all issues for this current proj
        all_issues_for_curr_proj = pull_all_issues_for_a_proj(project_id)

        # compute time for all the issues in this current project
        all_issue_time_dict = calc_time_from_multiple_issues(all_issues_for_curr_proj)
        
        # invoke the function that converts seconds to human time
        # for each issue in project per date per user
        humantime_lst_per_date = convert_to_human_time_proj_issues(
            all_issue_time_dict)


        # aggregate all the issue times from the project
        final_time_dict = aggregate_issue_times_across_a_proj(humantime_lst_per_date)

        # build the list of times for all issues for all projs
        if sum_flatten(final_time_dict):
            grand_list.append(final_time_dict)
    
    return grand_list


def calc_time_from_issue_notes(projID, issueIID):
    """
    Given a single ticket, using the gitlab API, read the ticket and all comments on it
    Get all the notes from an issue 
    param : theURL the endpoint, issueIID
    return: output the JSON response
    """

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
        time_substr = 'of time spent'
        # regex patterns
        time_info_pattern = r'(^added|subtracted).*of\stime\sspent\sat\s\d+-\d+-\d+$'
        time_removed_pattern = r'(^removed\stime\sspent$)'

        # check if a time spent information is in the note body else skip
        if re.match(time_info_pattern, note_body):
            # extract username and date
            note_author = each_note["author"]["name"]
            date_time_created = each_note['created_at']

            # concatenate the notebody with username
            concat_notes = (note_body) + ' ' + (note_author)

            # preprocess the date
            dt = dateutil.parser.parse(date_time_created)
            date_time_logged = '%4d-%02d-%02d' % (dt.year, dt.month, dt.day)

            # extract time phrase
            split_at_indx = concat_notes.find(time_substr)
            time_phrase = concat_notes[:split_at_indx-1]

            # parse time phrase using the timeparse module and return number of seconds
            total_seconds = pytimeparse.timeparse(time_phrase)

            if (total_seconds >= 0):
                pos_time = total_seconds
            else:
                neg_time = -(total_seconds)

            final_ouput_dict.setdefault(note_author, []).append(
                {'date': date_time_logged, "positivetime": pos_time, "negativetime": neg_time, "proj#": projID})
        
        # reset flag - reset all the values to 0 for every author; up to this day
        if re.match(time_removed_pattern, note_body):
            # extract who removed time spent info and the date
            note_author = each_note["author"]["name"]
            date_time_created = each_note['created_at']

            # concatenate the notebody with username
            concat_notes = (note_body) + ' ' + (note_author)

            # preprocess the date
            dt = dateutil.parser.parse(date_time_created)
            date_time_logged = '%4d-%02d-%02d' % (dt.year, dt.month, dt.day)

            # this case has been decided that it won't affect the time record
            # final_ouput_dict = {} # reset all times

            # just for information
            # print('Time info has been cleared on: ',
            #       date_time_logged, "for project# ", projID, "for issue#", issueIID, ' by ', note_author)

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
        time_spent_info_seconds = aggregate_time_spent_per_issue_per_user(
            issue_notes_time_dict)
        
        if sum_flatten(time_spent_info_seconds):
            # populate the list, if not empty
            extracted_time_info_list.append(time_spent_info_seconds)

    return extracted_time_info_list


def aggregate_time_per_issue_per_user_per_date(result_dict):
    """
    Calculate the time spent for a single issue for every user 
    produce a 2D output of date and the corresponding time spent information for each user
    on that date
    """

    # further process the result
    time_spent_dict_per_user = {}

    for each_user, each_time_lst in result_dict.items():
       
       if each_user not in time_spent_dict_per_user:
            time_spent_dict_per_user[each_user] = []
            
            for each_lst_item in each_time_lst:
                time_dict = {}
                # new user time info for this day
                if not any(each_lst_item['date'] in d['date'] for d in time_spent_dict_per_user[each_user]):
                    # if the time info is not there, get the info
                    time_dict['date'] = each_lst_item['date']
                    time_dict['proj_id'] = each_lst_item['proj#']
                    time_dict['tot_pos_sec'] = each_lst_item['positivetime']
                    time_dict['tot_neg_sec'] = each_lst_item['negativetime']
                    time_dict['proj_id'] = each_lst_item['proj#']
                    
                    time_spent_dict_per_user[each_user].append(time_dict)
                # add existing user info for this day
                else:
                    date_indx = next(i for i, d in enumerate(time_spent_dict_per_user[each_user]) if d['date']==each_lst_item['date'])
                    # if there is an entry for that user, sum the time info as value
                    time_spent_dict_per_user[each_user][date_indx]['tot_pos_sec'] += each_lst_item['positivetime']
                    time_spent_dict_per_user[each_user][date_indx]['tot_neg_sec'] += each_lst_item['negativetime']
                
    return time_spent_dict_per_user



def aggregate_time_spent_per_issue_per_user(result_dict):
    """
    Calculate the time spent for a single issue for every user 
    produce a 2D output of date and the corresponding time spent information for each user
    on that date
    """

    # further process the result
    time_spent_dict_per_user = {}

    # final formatting should present dict of {user: {date: [positiveTimeLogged, negativeTimeLogged]}}
    for each_user, each_time_lst in result_dict.items():
        tmp_dict = {}  # intermediate dict
        for each_lst_item in each_time_lst:

            # new user time info for this day
            if (each_lst_item['date'] not in tmp_dict):
                time_dict = {}
                curr_date_to_dict = each_lst_item['date']
                # if the time info is not there, get the info
                time_dict['proj_id'] = each_lst_item['proj#']
                time_dict['tot_pos_time'] = each_lst_item['positivetime']
                time_dict['tot_neg_time'] = each_lst_item['negativetime']
                # time_dict['issue_id'] = each_lst_item['issue#']
                time_dict['proj_id'] = each_lst_item['proj#']
                # push the dict conataining time info into a temp dict with user as key
                tmp_dict[curr_date_to_dict] = time_dict
            # add existing user info for this day
            elif(each_lst_item['date'] in tmp_dict):
                # user to update
                update_date_in_dict = each_lst_item['date']
                # if there is an entry for that user, sum the time info as value
                tmp_dict[update_date_in_dict]['tot_pos_time'] += each_lst_item['positivetime']
                tmp_dict[update_date_in_dict]['tot_neg_time'] += each_lst_item['negativetime']
        if sum_flatten(tmp_dict):
            time_spent_dict_per_user.setdefault(each_user, []).append(tmp_dict)

    # maybe sort the final array based on dates before returning it
    return time_spent_dict_per_user


def aggregate_time_spent_per_issue(result_dict):
    """
    Calculate the time spent for a single issue for every user for the given date
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
                # time_dict['issue_id'] = each_lst_item['issue#']
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
        if sum_flatten(tmp_dict):
            time_spent_dict_per_date.setdefault(each_date, []).append(tmp_dict)

    # maybe sort the final array based on dates before returning it
    return time_spent_dict_per_date


def aggregate_issue_times_across_a_proj(issues_times_list):
    '''
    Aggregate all the time info across issues for the same project and produce a dict  
    output format: user, [{date, net_hrs, proj_id}, ...]
    '''
    aggregated_by_user_date_dict = {}
    for each_thing in issues_times_list:
        for each_user, time_info in each_thing.items():

            if each_user not in aggregated_by_user_date_dict:
                aggregated_by_user_date_dict[each_user] = []
                for each_lst_item in time_info:
                    for each_date, time_info_dict in each_lst_item.items():
                        tmp_dict = {}
                        if each_date not in tmp_dict:
                            tmp_dict['date'] = each_date
                            tmp_dict['net_hrs_spent'] = time_info_dict['net_hrs_spent']
                            tmp_dict['proj_id'] = time_info_dict['proj_id']
                            aggregated_by_user_date_dict[each_user].append(
                                tmp_dict)

                        else:
                            tmp_dict['net_hrs_spent'] += time_info_dict['net_hrs_spent']
                            aggregated_by_user_date_dict[each_user].append(
                                tmp_dict)
            else:
                for each_lst_item in time_info:
                    # add new dates from other issues
                    for each_date, time_info_dict in each_lst_item.items():
                        tmp_dict = {}
                        if not any(d['date'] == each_date for d in aggregated_by_user_date_dict[each_user]):
                            tmp_dict['date'] = each_date
                            tmp_dict['net_hrs_spent'] = time_info_dict['net_hrs_spent']
                            tmp_dict['proj_id'] = time_info_dict['proj_id']
                            aggregated_by_user_date_dict[each_user].append(
                                tmp_dict)
                        else:
                            # update net hours
                            dict_indx = next(i for i, d in enumerate(
                                aggregated_by_user_date_dict[each_user]) if d['date'] == each_date)
                            net_hrs_so_far = '%.002f' % float(
                                aggregated_by_user_date_dict[each_user][dict_indx]['net_hrs_spent'])
                            updated_net_hr = '%.002f' % (float(net_hrs_so_far) +
                                                         float(time_info_dict['net_hrs_spent']))

                            aggregated_by_user_date_dict[each_user][dict_indx]['net_hrs_spent'] = '%.002f' % float(
                                updated_net_hr)

    return aggregated_by_user_date_dict


def calculate_time_spent_per_proj(result_list):
    '''
    Calculate the time spent for a single proj for every user and every issue by date
    produce a 2D output of date and the corresponding time spent information for each user for all proj issues
    on that date
    '''
    all_issues_times = []

    for items in result_list:
        time_info_collection = aggregate_time_spent_per_issue(items)
        all_issues_times.append(time_info_collection)
    
    return all_issues_times


# def calculate_time_spent_per_proj_per_user(result_list):
#     '''
#     Calculate the time spent for a single proj for every user and every issue by user
#     produce a 2D output of date and the corresponding time spent information for each user for all proj issues
#     on that date
#     '''
#     all_issues_times = []

#     for items in result_list:
#         time_info_collection = aggregate_time_spent_per_issue_per_user(items)
#         all_issues_times.append(time_info_collection)

#     return all_issues_times


def batch_convert_to_hrs(time_dict):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable hrs format and put it into a dict
    '''
    total_time_hrs_dict = {}

    for user, user_times in time_dict.items():
        if user not in total_time_hrs_dict:
            total_time_hrs_dict[user] = []

            for time_record in user_times:
                hrs_dict = {}
                # new user time info for this day
                if not any(time_record['date'] in d['date'] for d in total_time_hrs_dict[user]):
                    # if the time info is not there, get the info
                    hrs_dict['date'] = time_record['date']
                    hrs_dict['proj_id'] = time_record['proj_id']
                    hrs_dict['tot_pos_hr'] = convert_to_hrs(
                        time_record['tot_pos_sec'])
                    hrs_dict['tot_neg_hr'] = convert_to_hrs(
                        time_record['tot_neg_sec'])
                    hrs_dict['net_hrs_spent'] = '%.002f' % (hrs_dict['tot_pos_hr'] -
                                                            hrs_dict['tot_neg_hr'])
                    
                    total_time_hrs_dict[user].append(hrs_dict)

    return total_time_hrs_dict



def convert_to_human_time(time_dict):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable (years, months, weeks,days,hours,mins and seconds) and put it back to a dict
    '''
    humantime_dict_per_date = {}

    for key, user_times in time_dict.items():
        tmp_dict = {}
        for each_user_in_dict in user_times:
            for each_user_key, eachtimeVal in each_user_in_dict.items():
                curr_user = each_user_key
                # grab the total seconds duration
                tot_pos_time = eachtimeVal['tot_pos_time']
                tot_neg_time = eachtimeVal['tot_neg_time']

                # grab the issue# and proj#
                #issue_id = eachtimeVal['issue_id']
                proj_id = eachtimeVal['proj_id']
                
                # convert the seconds to human time (.2f hrs)
                tot_pos_human_time = convert_to_hrs(tot_pos_time)
                tot_neg_human_time = convert_to_hrs(tot_neg_time)
                
                # calculate the net time
                net_seconds_spent = '%.002f' % (float(tot_pos_human_time) - float(tot_neg_human_time))
                
                tmp_dict[curr_user] = {'net_hrs_spent': net_seconds_spent,
                    'tot_pos_hrs': tot_pos_human_time, 'tot_neg_hrs': tot_neg_human_time, 'proj_id': proj_id}

        humantime_dict_per_date.setdefault(key, []).append(tmp_dict)

    return humantime_dict_per_date


def convert_to_human_time_proj_issues(time_lst):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable (years, months, weeks,days,hours,mins and seconds) and populate the list 
    of dictionaries for the project issues
    '''
    human_time_lst = []
    for each_obj in time_lst:
        human_time_lst.append(convert_to_human_time(each_obj))

    return human_time_lst


def convert_to_hrs(seconds):
    '''
    Convert seconds into hrs to 2 decimal places
    '''
    sign_string = '-' if int(seconds) < 0 else ''
    seconds = abs(int(seconds))

    hrs = round(seconds/3600, 2)
    converted_hrs = '%s%.002f' % (sign_string, hrs)
    return float(converted_hrs)


def sum_flatten(stuff): return len(sum(map(list, stuff), []))
    

def export_to_csv(input_dict, filename):
    '''
    take the time info and user dictionary output and process it
    write a csv file as output in the current directory
    '''
    with open( filename +'.csv', mode='w') as csv_file:
        fields = ['Employee', 'Date', 'Net Hours', 'Project ID']

        writer = csv.DictWriter(csv_file, fieldnames=fields, extrasaction='ignore')

        # write the header to the csv
        writer.writeheader()

        # iterate through the output dict/json object and prep csv
        for user, user_info in sorted(input_dict.items()):
            for items in user_info:
                row = {'Employee': user, 'Date': items['date'], 'Net Hours': items['net_hrs_spent'], 'Project ID': items['proj_id']}
                    # row.update(val)
                writer.writerow(row)

    return filename + '.csv'

def make_dates_columns(filename):
    '''
    Transpose/pivot the the csv and bring the dates as columns 
    '''
    df = pandas.read_csv(filename, sep=',') # read in the csv file generated
    acc_numbers = pandas.read_csv('account_numbers.csv') # read in the account numbers csv

    transposed_df = df.pivot(index='Employee', columns='Date',values='Net Hours').fillna(0)
    
    ready_df = pandas.merge(acc_numbers, transposed_df, how='right', left_on=[
                            'Employee'], right_on=['Employee']).fillna(0)

    ready_df.to_csv(filename, sep=',')
    
    return ready_df

def export_issue_info(proj_id_str, issue_id_str):
    '''
    export a list of time info for a specific issue within a project
    '''
    # get list of notes and a few other relevant info
    time_dict = calc_time_from_issue_notes(proj_id_str, issue_id_str)

    # invoke the function that aggregates time spent info for users summarized to the day
    time_info_seconds = aggregate_time_per_issue_per_user_per_date(time_dict)

    # invoke the function that converts seconds to human time for each date
    time_dict_hrs = batch_convert_to_hrs(time_info_seconds)

    # export aggregated user - time data as a csv
    csv_out = export_to_csv(time_dict_hrs, 'proj_' + proj_id_str + '_issue_' + issue_id_str)

    # make the dates the columns of the csv
    make_dates_columns(csv_out)

def export_proj_issues_info(proj_id_str):
    '''
    export the time info for all the issues for a specific project
    '''
    # get list of time info from all the notes in all the issues 
    all_issues_lst = pull_all_issues_for_a_proj(proj_id_str)
    
    # get the times from all the issues 
    time_dict = calc_time_from_multiple_issues(all_issues_lst)
    
    # invoke the function that converts seconds to human time
    # for each issue in project per date per user
    humantime_lst_per_date = convert_to_human_time_proj_issues(time_dict)
    
    # aggregate all the issue times from the project
    final_time_dict = aggregate_issue_times_across_a_proj(humantime_lst_per_date)

    # export aggregated time info for each user**
    filename_csv = 'user_times_proj' + proj_id_str
    csv_output = export_to_csv(final_time_dict, (filename_csv))
    
    # make the dates the columns of the csv
    make_dates_columns(csv_output)

def export_all_time_info():
    '''
    export a list of time info for a all projects and issues
    '''
    # compute the time info for all issues and projects
    all_time_info = pull_all_project_all_issues()

    # for each project export a csv record
    i =0
    for each_record in all_time_info:
        filename_csv = 'user_times_proj_'
        proj_id = [item['proj_id'] for d_ in each_record.values() for item in d_]
        tmp_csv = export_to_csv(each_record, (filename_csv + str(proj_id[0]))) # convert dicts to csv
        make_dates_columns(tmp_csv) # transpose dates as columns
        i += 1

def main():
    """
    The main function
    """
    # prompt user for inputs
    # proj_id_str = input('Type the project ID or hit enter to skip: ')
    # issue_id_str = input('Type the Issue ID or hit enter to skip: ')

    # TESTING 
    proj_id_str = ''
    issue_id_str = ''

    if proj_id_str !='' and issue_id_str !='':
        # time info for an issue
        export_issue_info(proj_id_str, issue_id_str)
    
    elif proj_id_str != '' and issue_id_str =='':
        # time info for all issues in the project
        export_proj_issues_info(proj_id_str)
  
    else:
        # time info for all the issues in all projects 
        export_all_time_info()

# invoke the main method
main()