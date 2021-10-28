""" Scripts to run program related to filing url data
# Cadence: Monthly? At least Quarterly
# LOADS SEC IDX FILE OF ALL QUARTERLY FILINGS
# Reads in SEC filing idx files

read_idx_files():
    - opens new idx files and adds NPORT filing urls to master_urls.pkl
gen_ncen():
    - opens all idx files and adds all NCEN filings urls to master_ncens.pkl
gen_allfiles():
    - opens lal idx files and adds all filing urls to all_filings.pkl

# TO DO Combine gen_ncen with read_idx_files into one script

"""


import os
import pandas as pd

def create_dfs(overwrite=False):

    allfilename = 'filings/all_filings.pkl'
    all_cols = ['CIK Number', 'company_name', 'form_type', 'fileDate', 'filingURL']
    if ~os.path.exists(allfilename) or overwrite:
        all_filings = pd.DataFrame(columns=all_cols)
        all_filings.to_pickle(allfilename)

    urlfilename = 'master_urls.pkl'
    url_cols = ['CIK Number', 'company_name', 'filingURL', 'form_type', 'fileDate', 'valDate', 'accessNum', 'seriesid']
    if ~os.path.exists(urlfilename) or overwrite:
        master_urls = pd.DataFrame(columns=url_cols)
        master_urls.to_pickle(urlfilename)


def read_idx_files():

    ignorefile = 'filings/ignorelist.csv'
    ignorelist = pd.read_csv(ignorefile)
    urlbegin = 'https://www.sec.gov/Archives/'

    urlfilename = 'master_urls.pkl'
    master_urls = pd.read_pickle(urlfilename)

    master_dir = os.getcwd().replace('\\', '/') + '/filings'

    for filename in os.listdir(master_dir):

        if filename not in list(ignorelist['loadedfiles']) and filename[-3:]=='idx':

            #  Read in idx file
            print(filename)
            tmp = pd.read_table('filings/'+filename)
            tmp = tmp[6:]
            tmp = tmp.iloc[:, 0].str.split('|', expand=True)
            colmap = {0: 'CIK Number', 1: 'company_name', 2: 'form_type', 3: 'fileDate', 4: 'filingURL'}
            tmp.rename(columns=colmap, inplace=True)

            # Filter for NPORT filings
            subtmp = tmp[(tmp['form_type'] == 'NPORT-P') |
                         (tmp['form_type'] == 'NPORT-P/A') |
                         (tmp['form_type'] == 'NT NPORT-P')].copy()
            subtmp['filingURL'] = urlbegin+subtmp['filingURL']
            master_urls = master_urls.append(subtmp, ignore_index=True)

            # if final file for each quarter, add to ignorelist
            if len(filename) == 14:
                ignorelist.loc[len(ignorelist), 'loadedfiles'] = filename

            print('Done loading', filename)

    master_urls.drop_duplicates(inplace=True, ignore_index=True)
    master_urls.to_pickle(urlfilename)
    ignorelist.to_csv(ignorefile, index=False)

def gen_ncen():

    urlbegin = 'https://www.sec.gov/Archives/'

    ncen_filename = 'master_ncens.pkl'
    master_ncens = pd.read_pickle(ncen_filename)

    master_dir = os.getcwd().replace('\\', '/') + '/filings'

    for filename in os.listdir(master_dir):

        if filename[-3:]=='idx':

            #  Read in idx file
            print(filename)
            tmp = pd.read_table('filings/'+filename)
            tmp = tmp[6:]
            tmp = tmp.iloc[:, 0].str.split('|', expand=True)
            colmap = {0: 'CIK', 1: 'company_name', 2: 'form_type', 3: 'fileDate', 4: 'filingURL'}
            tmp.rename(columns=colmap, inplace=True)

            # Filter for NPORT filings
            subtmp = tmp[(tmp['form_type'] == 'N-CEN') |
                        (tmp['form_type'] == 'N-CEN/A') |
                        (tmp['form_type'] == 'NT N-CEN')|
                        (tmp['form_type'] == 'NT-NCEN') |
                        (tmp['form_type'] == 'NT-NCEN/A')].copy()
            subtmp['filingURL'] = urlbegin+subtmp['filingURL']
            master_ncens = master_ncens.append(subtmp, ignore_index=True)

            print('Done loading', filename)

    master_ncens.drop_duplicates(inplace=True, ignore_index=True)
    master_ncens.to_pickle(ncen_filename)


def gen_allfiles():

    allfilename = 'filings/all_filings.pkl'
    urlbegin = 'https://www.sec.gov/Archives/'

    master_dir = os.getcwd().replace('\\', '/') + '/filings'

    for filename in os.listdir(master_dir):

        if filename[-3:]=='idx':

            #  Read in idx file
            print(filename)
            tmp = pd.read_table('filings/'+filename)
            tmp = tmp[6:]
            tmp = tmp.iloc[:, 0].str.split('|', expand=True)
            colmap = {0: 'CIK', 1: 'company_name', 2: 'form_type', 3: 'fileDate', 4: 'filingURL'}
            tmp.rename(columns=colmap, inplace=True)

            # if final file for each quarter, append to all_filings and add to ignorelist
            if len(filename) == 14:
                # master____.idx (i.e. does not have _todate in name)
                # don't want to drop duplicates everytime for this database
                all_filings = pd.read_pickle(allfilename)
                all_filings = all_filings.append(tmp)
                all_filings.drop_duplicates(inplace=True, ignore_index=True)
                all_filings.to_pickle(allfilename)

            print('Done loading', filename)



def main():
    read_idx_files()

if __name__ == "__main__":
    main()
    # get_series_id()