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
    8: 'GA014033',
    9: 'BA019044',
    10: 'KA014000',
    11: 'LA014099',
    12: 'ZA014011'
    }

# mapping rules
def map_accounts (row):
    proj_id = pd.to_numeric(row['ProjID'])
    if proj_id < 20 :
        return mapdict[2]
    if proj_id > 20 & proj_id < 40:
        return mapdict[3]
    if proj_id > 40 & proj_id < 60:
        return mapdict[4]
    if proj_id > 60 & proj_id < 80:
        return mapdict[5]
    if proj_id > 80 & proj_id < 100:
        return mapdict[6]
    if proj_id > 100 & proj_id < 120:
        return mapdict[7]
    if proj_id > 120 & proj_id < 140:
        return mapdict[8]
    if proj_id > 120 & proj_id < 160:
        return mapdict[9]
    if proj_id > 190 & proj_id < 210:
        return mapdict[10]
    if proj_id > 220 & proj_id < 261:
        return mapdict[11]
    if proj_id < 262:
        return mapdict[12]
    else:
        return mapdict[1]


def map_project_to_account(input_file, output_file, print_to_console_or_no):    
    '''
    Map the project id with the respective account number

    '''
    final_cols = ['Name', 'Account', 'Total']

    csv_input_df = pd.read_csv(input_file)

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

    # re-arrange columns
    arranged_columns = csv_input_df.columns.tolist()
    arranged_columns.remove('Name')
    arranged_columns.remove('Account')
    arranged_columns.remove('Total')
    
    # construct dataframe with selected columns
    final_cols.extend(arranged_columns)
    final_df = csv_input_df[final_cols]
    
    # attempts to aggregate
    final_df = final_df.groupby(['Name', 'Account']).sum().reset_index()

    # write to CSV file
    final_df.to_csv(output_file, index=False, na_rep='0.00', float_format='%.2f')

    # print output to console
    if (print_to_console_or_no):
        print(final_df)

    return final_df


def main():
    """
    The main function
    """
    # if __name__ == "__main__":
    
    # default values if not provided
    FILENAME = 'timesheet.csv'
    OUTPUT = 'False'

    parser = argparse.ArgumentParser(prog='account_mapper.py')

    parser.add_argument('-v','--version', action='version', version='%(prog)s v1.00')
    parser.add_argument('-o', dest='output',
                        help='specify output file.', nargs='?', const='Payroll_.csv', default=FILENAME)
    parser.add_argument('-i', dest='input',
                        help='specify input file.', nargs='?', const='timesheet.csv', default=FILENAME)
    parser.add_argument('-p', dest='stdout',
                        help='Output to std out.', nargs='?', const='True', default=OUTPUT)

    args = parser.parse_args()

    # extract the CLI arguments
    out_file = args.output
    in_file = args.input
    print_to_console_or_no = args.stdout

    # call the function with the values extracted
    map_project_to_account(in_file, out_file, print_to_console_or_no)


# invoke the main method
main()