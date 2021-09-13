# SCRAPS CBINSIGHTS UNICORN LIST
# Cadence: Quarterly?

import pandas as pd

unicorn_url = 'https://www.cbinsights.com/research-unicorn-companies'
data1 = pd.read_html(unicorn_url)[0]

unicorn_filename = 'master_unicorns.xlsx'
old_unicorns = pd.read_excel(unicorn_filename)

rename_cols = {'Company': 'Company Name', 'Valuation ($B)': 'Valuation'}
keep_cols = ['Company Name','aka', 'Legal Name', 'Ignore', 'Checked']

data2 = data1.rename(columns=rename_cols).merge(old_unicorns[keep_cols], how='left', on='Company Name').reindex(columns=old_unicorns.columns)
data2 = data2.fillna('')

data2.to_excel(unicorn_filename, index=False)