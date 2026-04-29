#!/usr/bin/env python3
import os
import logging
import requests
import json
import pandas as pd
from datetime import date
from dotenv import load_dotenv
load_dotenv()

nbim_api = os.getenv('NBIM_API_KEY')
url = 'https://vd.a.nbim.no'
header = {'x-api-key': nbim_api}
companies = '/v1/ds/tickers' # tickers list

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tickers_list_request.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info('Starting requesting tickers')
        r = requests.get(url=f'{url}{companies}', headers=header)
        table = pd.DataFrame(json.loads(r.content))
        if table.status.companies == 'success':
            company_names = table.dstickers.companies
            c_names = [item.get("t") for item in company_names]
            c_names_df = pd.DataFrame(c_names, columns=['ticker'])
            c_names_df['date'] = date.today()
            c_names_df.to_csv('data/tickers.csv')
            logger.info(f"Success with requesting tickers. Total tickers: {len(c_names)}. Tickers saved to data/tickers.csv")
        else:
            logger.error(f"Error with requesting tickers: {table.message.messageString}")
            return None
    except Exception as e:
            logger.error(f"Error with API request: {e}")
            return None

if __name__ == "__main__":
    main()