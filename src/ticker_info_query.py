import os
from pathlib import Path
import logging
import requests
import json
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

nbim_api = os.getenv('NBIM_API_KEY')
url = 'https://vd.a.nbim.no'
header = {'x-api-key': nbim_api}
ticker_info = '/v1/query/ticker/' # Ticker meetings
input_file = 'data/tickers.csv'
output_file = 'data/tickers_info.csv'
failed_ticker = 'data/failed_tickers.csv'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tickers_info_query.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_existing_data(output_file) -> pd.DataFrame:
        """Load existing tickers if available"""
        output_file = Path(output_file)
        if output_file.exists():
            try:
                existing_df = pd.read_csv(output_file)
                logger.info(f"Loaded existing data with {len(existing_df)} records")
                return existing_df
            except Exception as e:
                logger.warning(f"Failed to load existing data: {e}")
        return pd.DataFrame()

def should_scrape(ticker: str, existing_df: pd.DataFrame) -> bool:
        "Check if ticker needs to be queried"
        if existing_df.empty:
            return True
        # Check if ticker already exists
        mask = (existing_df['ticker'] == ticker)
        return not mask.any()
           
def query_ticker_info(output_file):
    logger.info(f"Loading input file: {input_file}")
    input_df = pd.read_csv(input_file)
    logger.info(f"Total rows in input CSV: {len(input_df)}")

    # Load existing data if available
    existing_df = load_existing_data(output_file)

    # Process each name
    skipped_count = 0
    processed_count = 0
    failed_tickers = []

    for index, row in tqdm(input_df.iterrows(), total=len(input_df), desc="Processing tickers info"):
        ticker = row.get('ticker', '')
        
        processed_count += 1

        # Check if we need to scrape this ticker
        if not should_scrape(ticker, existing_df):
            skipped_count += 1
            logger.debug(f"Skipping {ticker} - already exists")
            continue

        # Query the ticker info
        all_tickers_rows = []

        try:
            result = requests.get(url=f'{url}{ticker_info}{ticker}', headers=header)
            
            if result.status_code==429:
                logger.error("API rate limit exceeded (429) - stopping")
                break 

            if result.status_code != 200:
                logger.error(f"Request for {ticker} failed with status code {result.status_code}")
                failed_tickers.append(ticker)
                continue
            
            data = pd.DataFrame(json.loads(result.content))
            if data.status[0] == 'success':
                ticker_data = data.companies[0]            
                meetings_data = ticker_data.get('meetings', [])
                for meeting in meetings_data:
                    row = {
                        'ticker': ticker,
                        'ticker_': ticker_data.get('ticker') if ticker_data else "",
                        'country': ticker_data.get('country') if ticker_data else "",
                        'id': ticker_data.get('id') if ticker_data else "",
                        'isin': ticker_data.get('isin') if ticker_data else "", 
                        'meetingDate': meeting.get('meetingDate') if meeting else "",
                        'meetingId': meeting.get('meetingId') if meeting else "",
                        'meetingType': meeting.get('meetingType')if meeting else ""
                    }
                    all_tickers_rows.append(row)
                processed_count += 1

            elif data.empty and not 'companies':
                failed_tickers.append(ticker)
                logger.warning(f"No tickers data found for: {ticker}")
                
            elif data.message.messageString == 'LimitExceeded':
                failed_tickers.append(ticker)
                logger.error("API limit exceeded")
                break

        except Exception as e:
            logger.error(f"Unexpected error for {ticker}: {e}")
            failed_tickers.append(ticker)
            continue

        try:
            df = pd.DataFrame(all_tickers_rows)
            # Append to existing file or create new one
            output_file = Path(output_file)
            if output_file.exists():
                df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8')
            else:
                df.to_csv(output_file, index=False, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to save product data: {e}")

                
        # Update existing_df to avoid duplicates in current session
        existing_df = pd.concat([existing_df, pd.DataFrame(all_tickers_rows)], ignore_index=True)
            
    logger.info("Scraping completed")
    logger.info(f"Total processed: {processed_count}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Failed: {len(failed_tickers)}, company names saved to {failed_ticker}")
    
    if failed_tickers:
        failed_tickers_df = pd.DataFrame(failed_tickers)
        failed_tickers_df.to_csv(failed_ticker, mode='a', header=False, index=False, encoding='utf-8')

def main():
    logger.info("Starting companies info quering")
    query_ticker_info(output_file)

if __name__ == "__main__":
    main()