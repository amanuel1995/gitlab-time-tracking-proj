import csv
import pandas as pd
import argparse

mapdict = {
    1: 'UNASSIGNED',
    2: 'GA014441',
    3: 'RC108057',
    4: 'RC107995',
    5: 'GC108057',
    6: 'GA013721',
    7: 'RC108000',
    8: 'GA014000'
    }

# Ampping rules
def map_accounts (row):
    if row['ProjID'] == 10 :
        return mapdict[2]
    if row['ProjID'] < 10 :
        return mapdict[3]
    if row['ProjID'] > 10 & row['ProjID'] < 25 :
        return mapdict[4]
    if row['ProjID'] > 25 & row['ProjID'] < 45 or row['ProjID'] == 143:
        return mapdict[5]
    if row['ProjID'] == 149 & row['ProjID'] == 29 or row['ProjID'] == 175:
        return mapdict[6]
    if row['ProjID'] > 45 & row['ProjID'] < 100 or row['ProjID'] == 12 or row['ProjID'] == 13 or row['ProjID'] == 257:
        return mapdict[7]
    if row['ProjID'] > 100 & row['ProjID'] < 121 or row['ProjID'] == 21 or row['ProjID'] == 90:
        return mapdict[8]
    return mapdict[1]


def map_project_to_account(csv_file, mapdict):    
    '''
    Map the project id with the respective account number

    '''
    final_cols = ['Name', 'Account', 'Total']

    csv_input_df = pd.read_csv(csv_file)

    # Mapping Proj ID to Account #
    csv_input_df['Account'] = csv_input_df.apply(lambda row: map_accounts(row), axis=1)

    previous_cols = csv_input_df.columns.tolist()

    # remove project ID and project name columns from columns list
    # to add it in the right order later
    previous_cols.remove('Project')
    previous_cols.remove('ProjID')
    
    csv_input_df = csv_input_df[previous_cols]

    # reorder columns by dates  
    csv_input_df = csv_input_df.reindex(
        sorted(csv_input_df.columns), axis=1)

    arranged_columns = csv_input_df.columns.tolist()
    arranged_columns.remove('Name')
    arranged_columns.remove('Account')
    arranged_columns.remove('Total')
    
    final_cols.extend(arranged_columns)
    

    final_df = csv_input_df[final_cols]
    
    return final_df

print(map_project_to_account('payroll_2019-04-01_to_2019-04-18.csv', mapdict))
