# set interpreter and encoding
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import the important modules
import argparse
import time
import pandas
import csv
import re
import json
import dateutil.parser
import pytimeparse
import config
import requests
from datetime import datetime, timedelta
startTime = datetime.now()

#################################################################
# endpoints for GitLab API V.4
# issues url
issues_url = "https://gitlab.matrix.msu.edu/api/v4/issues"

# projects url
proj_url = "https://gitlab.matrix.msu.edu/api/v4/projects"

# users url
users_url = "https://gitlab.matrix.msu.edu/api/v4/users"

#################################################################
# CONSTANTS
MAXOBJECTSPERPAGE = 100  # Gitlab Pagination max
DEFAULTPERPAGE = 20     # Preferred items per page number
#################################################################

# params to inject while sending a GET request
payload = {'per_page': MAXOBJECTSPERPAGE}
#################################################################


def pull_api_response(endpoint):
    """
    py:function:: pull_api_response(endpoint)

    Loop through the pages and collect the entire response from API endpoint
    return a list object containing api response

    :param str endpoint : the end point from which the api response is fetched
    :return: list of the response objects
    :rtype: list
    :raises requests.ConnectionError: if there is no internet connection to endpoint
    :raises requests.Timeout: if the request timed out and no response was sent
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
    
    # handle pagination where the response is multiple pages
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


def pull_all_project_all_issues():
    '''
    Pull all projects list from the matrix gitlab
    return list of all the projects
    '''

    endpoint = proj_url + '/?sort=asc'
    all_projs = pull_api_response(endpoint)

    return all_projs


def calc_time_from_issue_notes(proj_id, issueIID, proj_name):
    """
    Given a single ticket, read the ticket and all comments on it
    Get all the time info from an issue

    :param str projID : the project ID
    :param str issueIID : the issue ID
    :return: the JSON response as list
    :rtype: list
    """

    # build the URL endpoint and extract notes in the issue
    built_endpoint = proj_url + '/' + proj_id + '/issues/' + \
        issueIID + '/notes' + '?sort=asc&order_by=updated_at'

    notes_json_res = pull_api_response(built_endpoint)

    concat_notes = ""

    final_ouput_dict = {}
    # has unique dates as key and list of dicts as value

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

            # parse time phrase using the timeparse module and return seconds
            total_seconds = pytimeparse.timeparse(time_phrase)

            if (total_seconds >= 0):
                pos_time = total_seconds
            else:
                neg_time = -(total_seconds)

            final_ouput_dict.setdefault(note_author, []).append(
                {'date': date_time_logged, "positivetime": pos_time, 
                 "negativetime": neg_time, "proj_name": proj_name, "proj_id": proj_id})
        
        # check if a time removed information is in the note body
        if re.match(time_removed_pattern, note_body):
            # this case has been decided that it won't affect the time record
            pass
        
        else:
            pass

        pos_time, neg_time = 0, 0  # Reset counters

    return final_ouput_dict


def calc_time_from_multiple_issues(proj_issues_list, proj_name):
    '''
    Calculate the time from every issue for a given project
    :param list proj_issues_list : the list of a project issues
    :return: list of time info
    :rtype: list
    '''
    extracted_time_info_list = []

    # loop through each issue in that project
    for each_item in proj_issues_list:
        issue_iid = str(each_item['iid'])
        proj_id = str(each_item['project_id'])

        # call the function to extract time info from each note
        issue_notes_time_dict = calc_time_from_issue_notes(
            proj_id, issue_iid, proj_name)

        # aggregate time spent for every issue
        time_spent_info_seconds = aggregate_time_spent_per_issue_per_user(
            issue_notes_time_dict)
        
        if sum_flatten(time_spent_info_seconds):
            # populate the list, if not empty
            extracted_time_info_list.append(time_spent_info_seconds)

    return extracted_time_info_list


def aggregate_time_spent_per_issue_per_user(result_dict):
    """
    Calculate the time spent for a single issue for every user 
    and produce a 2D output of date and the corresponding time spent
    information for each user on that date.

    :param dict result_dict : the dictionary of user:times 
    :return: dict of hrs logged in + and -
    :rtype: dict
    """

    # further process the result
    time_spent_dict_per_user = {}

    # final formatting should present dict of 
    # {user: {date: [positiveTimeLogged, negativeTimeLogged]}}
    for each_user, each_time_lst in result_dict.items():
        tmp_dict = {}  # intermediate dict
        for each_lst_item in each_time_lst:

            # new user time info for this day
            if (each_lst_item['date'] not in tmp_dict):
                time_dict = {}
                curr_date_to_dict = each_lst_item['date']
                # if the time info is not there, get the info
                time_dict['proj_name'] = each_lst_item['proj_name']
                time_dict['tot_pos_time'] = each_lst_item['positivetime']
                time_dict['tot_neg_time'] = each_lst_item['negativetime']
                time_dict['proj_id'] = each_lst_item['proj_id']

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

    return time_spent_dict_per_user


def aggregate_time_spent_per_issue(result_dict):
    """
    Calculate the time spent for a single issue for every user for the given date
    produce a 2D output of date and the corresponding time spent information for each user
    on that date.

    :param dict result_dict : the dictionary from another function
    :return: 2D dict of hrs logged info vs user
    :rtype: dict
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
                time_dict["proj_name"] = each_lst_item["proj_name"]
                time_dict["proj_id"] = each_lst_item["proj_id"]
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

    return time_spent_dict_per_date


def aggregate_issue_times_across_a_proj(issues_times_list):
    '''
    Aggregate all the time info across issues for the same project and produce a dict  
    output format: user, [{date, net_hrs, proj_id}, ...]

    :param list issues_times_list : list of issues for 1 project
    :return: aggregated dict
    :rtype: dict

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
                            tmp_dict['proj_name'] = time_info_dict['proj_name']
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
                            tmp_dict['proj_name'] = time_info_dict['proj_name']
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
    on that date.

    :param list result_list : list of dicts containing time info
    :return: all issues times in a list
    :rtype: list
    '''
    all_issues_times = []

    for items in result_list:
        time_info_collection = aggregate_time_spent_per_issue(items)
        all_issues_times.append(time_info_collection)
    
    return all_issues_times


def batch_convert_to_hrs(time_dict):
    '''
    Take the dictionary, traverse it and convert the total seconds info to
    human readable hrs format and put it into a dict.

    :param dict tme_dict : dictionary containing the time info in seconds
    :return: the dict converted to hrs
    :rtype: dict
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
                    hrs_dict['proj_name'] = time_record['proj_name']
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
    Take a dictionary, traverse it and convert the total seconds info to
    human readable (hrs) and put it back to a dict.

    :param dict time_dict : the dictionary from last output 
    :return: dict of times converted to hrs with users
    :rtype: dict
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
                proj_id = eachtimeVal['proj_id']
                proj_name = eachtimeVal['proj_name']
                
                # convert the seconds to human time (.2f hrs)
                tot_pos_human_time = convert_to_hrs(tot_pos_time)
                tot_neg_human_time = convert_to_hrs(tot_neg_time)
                
                # calculate the net time
                net_seconds_spent = '%.002f' % (float(tot_pos_human_time) - float(tot_neg_human_time))
                
                tmp_dict[curr_user] = {'net_hrs_spent': net_seconds_spent,
                    'tot_pos_hrs': tot_pos_human_time, 'tot_neg_hrs': tot_neg_human_time, 'proj_id': proj_id,
                    'proj_name': proj_name}

        humantime_dict_per_date.setdefault(key, []).append(tmp_dict)

    return humantime_dict_per_date


def convert_to_hrs_proj_issues(time_lst):
    '''
    Take the dictionary, traverse it and convert the total seconds 
    info to human readable (hrs) and populate the list of dictionaries 
    for the project issues.
    '''
    human_time_lst = []
    
    for each_obj in time_lst:
        human_time_lst.append(convert_to_human_time(each_obj))

    return human_time_lst


def convert_to_hrs(seconds):
    '''
    Convert seconds into hrs and format to 2 decimal places.

    :param: integer or str
    :return: hrs from the seconds
    :rtype: float
    '''
    sign_string = '-' if int(seconds) < 0 else ''
    seconds = abs(int(seconds))

    hrs = round(seconds/3600, 2)
    converted_hrs = '%s%.002f' % (sign_string, hrs)
    
    return float(converted_hrs) # this could be bad?


def sum_flatten(stuff): 
    '''
    Check if the container is not empty by summing contents 
    in the container.

    :param: dict or list
    :return: bool true if not empty
    :rtype: bool
    '''
    return len(sum(map(list, stuff), []))
    

def export_to_csv(input_lst, filename):
    '''
    take the time info and user dictionary output and process it
    write a csv file as output in the current directory.

    :param list input_lst : the list of dictionaries to be written to csv
    :param str filename : the filename for the csv writer
    :return: filename concatenated with csv extension
    :rtype: str
    '''
    with open(filename + '.csv', mode='w') as csv_file:
        fields = ['Employee', 'Proj', 'ProjID', 'Date', 'Net Hours']

        writer = csv.DictWriter(
            csv_file, fieldnames=fields, extrasaction='ignore')

        # write the header to the csv
        writer.writeheader()

        # iterate through the output dict/json object and prep csv
        for item in input_lst:
            for user, user_info in sorted(item.items()):
                for items in user_info:
                    row = {'Employee': user, 'Proj': items['proj_name'], 
                    'ProjID': items['proj_id'],'Date': items['date'], 
                    'Net Hours': items['net_hrs_spent']}
                    # write the rows
                    writer.writerow(row)

    return filename + '.csv'


def make_dates_columns(filename, start_date, end_date):
    '''
    Transpose/pivot the the csv and bring the dates as columns.

    :param str filename : the file namee
    :param str start_date : initial date to filter by date
    :param str end_date : the last date to filter by date
    :return: dataframe with multi-index and dates as columns
    :rtype: pandas.core.frame.DataFrame 
    '''
    arranged_col = ['Name', 'Project', 'ProjID', 'Total']
    dates_col_lst = gen_dates_in_range(start_date, end_date)

    df = pandas.read_csv(filename, sep=',')  # read in the csv file generated

    # select the desired date range
    df = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # pivot_table around Date column
    df2 = df.pivot_table(index=['Employee', 'Proj','ProjID'],
                         columns='Date', fill_value='0.00')

    # save to CSV
    df2.to_csv(filename , sep=',')

    # read back and skip some rows
    df2 = pandas.read_csv(filename, skiprows=[0, 2])

    # rename column names
    df2.rename(columns={'Unnamed: 1': 'Project'}, inplace=True)
    df2.rename(columns={'Unnamed: 2': 'ProjID'}, inplace=True)
    df2.rename(columns={'Date': 'Name'}, inplace=True)

    # Split name into first & last name, swap first & last name position
    names = df2['Name']
    name_series = reverse_names(names)

    # replace the name column with swapped names series
    df2['Name'] = name_series

    my_columns = df2.columns.tolist()

    # reconstruct the dataframe with such an order of columns
    df2 = df2[my_columns]

    # add missing dates
    for n in range(len(dates_col_lst)):
        if dates_col_lst[n] not in df2:
            df2[dates_col_lst[n]] = 0.00

    # add the total column
    df2['Total'] = df2.drop('ProjID', axis=1).sum(axis=1)

    # re-arrange columns
    arranged_col.extend(dates_col_lst)
    df2 = df2[arranged_col]

    # Floating number issues ... limit to 2 decimal plcaes on display
    pandas.options.display.float_format = '{:,.2f}'.format

    # sort by last name?
    df2 = df2.sort_values('Name')

    # write final csv
    df2.to_csv(filename, index=False, na_rep='0.00', float_format='%.2f')

    return df2


def reverse_name(name):
    '''
    Take a pandas series object of full names and reverse last name first 
    and then the rest.
    '''
    split_name = name.split(" ")
    last_name = split_name[len(split_name)-1]
    first_name = split_name[0]

    # handle middle names, extract initials, append to first names after space
    if len(split_name) > 2:
        first_name = first_name + " " + split_name[1][0] + "."

    return last_name + " " + first_name


def reverse_names(names):
    return names.apply(reverse_name)


def export_all_time_info(d1,d2, filename, stdout = 'False'):
    '''
    export a list of time info for a all projects and issues.

    :param str d1 : start date for filtering records
    :param str d2 : end date for filtering the records
    :return: Nothing
    :rtype: None
    '''
    print('Sending request to Matrix GitLab Server ...')
    # compute the time info for all issues and projects
    all_projs = pull_all_project_all_issues()

    grand_list = []
    
    proj_counter = 1

    print(proj_counter, ' Processing the hours logged for the first Project ... ')
    # for each the project object in all_projs api response invoke the function to extract issues
    for each_project in all_projs:
        proj_id = str(each_project["id"])
        proj_name = each_project["name"]

        # pull all issues for this current proj
        all_issues_for_curr_proj = pull_all_issues_for_a_proj(proj_id)
        
        # compute time for all the issues in this current project
        all_issue_time_dict = calc_time_from_multiple_issues(
            all_issues_for_curr_proj, proj_name)
        
        # invoke the function that converts seconds to work hrs
        humantime_lst_per_date = convert_to_hrs_proj_issues(
            all_issue_time_dict)
        
        # aggregate all the issue times from the project
        final_time_dict = aggregate_issue_times_across_a_proj(
            humantime_lst_per_date)
        
        # build the list of times for all issues for all projs
        if sum_flatten(final_time_dict):
            grand_list.append(final_time_dict)
        proj_counter += 1
        print(proj_counter, ' Processing the hours logged from project named:', proj_name )
    
    print('Done')
    
    # produce a csv report
    tmp_csv = export_to_csv(grand_list, filename)
    final_out = make_dates_columns(tmp_csv,d1,d2)  # transpose dates as columns
    print('#####################################################')
    # if -p flag is set
    if stdout == 'True':
        print(final_out)

def valid_date(s):
    '''
    Function to check the passed dates' format validity.

    :param str s : date string
    :return: boolean
    :rtype: bool
    '''
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def gen_dates_in_range(start, end):
    dates = []

    d1 = datetime.strptime(start, '%Y-%m-%d')
    d2 = datetime.strptime(end, '%Y-%m-%d')
    
    # timedelta
    delta = d2 - d1         

    for i in range(delta.days + 1):
        d = d1 + timedelta(i)

        dates.append(datetime.strftime(d, '%Y-%m-%d'))
    return dates


def main():
    """
    The main function
    """
    if __name__ == "__main__":
    
        # default values if not provided
        TODAY = datetime.today().strftime('%Y-%m-%d')
        START = '2015-01-01'
        FILENAME = 'timesheet'
        OUTPUT = 'False'

        parser = argparse.ArgumentParser(prog='timesheet.py')

        parser.add_argument('-v','--version', action='version', version='%(prog)s v1.00')
        parser.add_argument('-d1', dest='date1',
                            help='choose the initial date for range. YYYY-MM-DD', type=valid_date, default=START)
        parser.add_argument('-d2', dest='date2',
                            help='choose the end date for range. YYYY-MM-DD', type=valid_date, default=TODAY)
        parser.add_argument('-o', dest='output',
                            help='Output to a file.', nargs='?', const='Payroll_', default=FILENAME)
        parser.add_argument('-p', dest='stdout',
                            help='Output to std out.', nargs='?', const='True', default=OUTPUT)

        args = parser.parse_args()
        
        d1 = args.date1.strftime('%Y-%m-%d')
        d2 = args.date2.strftime('%Y-%m-%d')
        
        filename = args.output
        stdout = args.stdout
        export_all_time_info(d1,d2,filename, stdout)


# invoke the main method
main()

print('Finished job in',(datetime.now() - startTime).seconds, " seconds.")
print('#####################################################')
