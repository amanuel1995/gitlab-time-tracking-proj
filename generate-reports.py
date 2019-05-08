import pandas as pd
import csv

def filter_by_user_or_proj(infilename, username='', project = '', outfilename='timesheet_filtered.csv'):
    '''
    Filter the result based on criteria like user and projects

    :param str filename : the file namee
    :param str project : project to filter by user
    :param str username : the username to filter ny
    :return: dataframe with desired user's info
    :rtype: pandas.core.frame.DataFrame 
    '''
    csv_input_df = pd.read_csv(infilename)
    
    # FILTERING: select the desired user

    # case 0: All hours from all users in all projects -- Done by default
    # case 1: All hours from all users in specific project/Account
    # case 2 : All hours for user x in all projects
    # case 2a : All hours for user x, y and z in all projects
    # case 2b : All hours for x y, and z users in all projects
    # case 3: All hours for user x in project y
    # case 3a: All hours for user x in projects x, y and z
    # case 3b: All hours for x,y and z users in a, b, and c projects/ accounts


    #  case 1
    if project != '' and username == '':
        csv_input_df2 = csv_input_df.loc[(csv_input_df['Account'] == project)]
    
    # case 2
    elif project =='' and username !='':
        csv_input_df2 = csv_input_df.loc[(csv_input_df['Name'] == username)]
    
    # case 3
    elif project != '' and username != '':
        csv_input_df2 = csv_input_df.loc[(csv_input_df['Name'] == username) & (
            csv_input_df['Account'] == project)]
    
    # write final csv
    # csv_input_df2.to_csv(outfilename, index=False,
    #                      na_rep='0.00', float_format='%.2f')

    return csv_input_df2


print(filter_by_user_or_proj('payroll_2019-04-01_to_2019-04-30_mapped.csv','Goshu Amanuel', 'GA014441', 'filtered_timesheet.csv'))

print(filter_by_user_or_proj('payroll_2019-04-01_to_2019-04-30_mapped.csv', '', 'GA014441', 'filtered_timesheet.csv'))

print(filter_by_user_or_proj('payroll_2019-04-01_to_2019-04-30_mapped.csv','Goshu Amanuel', '' ,'filtered_timesheet.csv'))
