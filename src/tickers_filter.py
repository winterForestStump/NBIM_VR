# Script for filtering duplicates from tickers_info.csv file
# The script compares isins from company_info.csv and tickers_info.csv
# Resulted list of tickers saved to csv file

import pandas as pd

tickers_info = pd.read_csv('data/tickers_info.csv')
companies_info = pd.read_csv('data/company_info.csv')

companies_info_unique = set(companies_info['isin'])
tickers_info_unique = set(tickers_info['isin'])

tickers = list(tickers_info_unique - companies_info_unique)

tickers_info_ = tickers_info[tickers_info['isin'].isin(tickers)]

tickers_info_.to_csv('data/tickers_info.csv')
print(f'Saved {len(tickers_info_)} to data/tickers_info.csv')