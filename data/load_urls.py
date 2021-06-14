import pandas as pd
import os


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

    allfilename = 'filings/all_filings.pkl'
    ignorefile = 'filings/ignorelist.csv'
    ignorelist = pd.read_csv(ignorefile)
    urlbegin = 'https://www.sec.gov/Archives/'

    urlfilename = 'master_urls.pkl'
    master_urls = pd.read_pickle(urlfilename)

    master_dir = os.getcwd().replace('\\', '/') + '/filings'

    for filename in os.listdir(master_dir):

        if filename not in ignorelist and filename != 'ignorelist.csv':

            tmp = pd.read_table('filings/'+filename)
            tmp = tmp[6:]
            tmp = tmp.iloc[:, 0].str.split('|', expand=True)
            colmap = {0: 'CIK', 1: 'company_name', 2: 'form_type', 3: 'fileDate', 4: 'filingURL'}
            tmp.rename(columns=colmap, inplace=True)

            if len(filename) == 14:
                # master____.idx (i.e. does not have _todate in name)
                # dont' want to drop duplicates everytime for this database
                all_filings = pd.read_pickle(allfilename)
                all_filings = all_filings.append(tmp)
                all_filings.drop_duplicates(inplace=True, ignore_index=True)
                all_filings.to_pickle(allfilename)

            subtmp = tmp[(tmp['form_type'] == 'NPORT-P') |
                         (tmp['form_type'] == 'NPORT-P/A') |
                         (tmp['form_type'] == 'NT NPORT-P')].copy()
            subtmp['filingURL'] = urlbegin+subtmp['filingURL']
            # subtmp.drop(columns='company_name', inplace=True)
            master_urls = master_urls.append(subtmp, ignore_index=True)
            print('Done loading', filename)

            ignorelist.loc[len(ignorelist), 'loadedfiles'] = filename

    master_urls.drop_duplicates(inplace=True, ignore_index=True)
    master_urls.to_pickle(urlfilename)
    ignorelist.to_csv(ignorefile)
