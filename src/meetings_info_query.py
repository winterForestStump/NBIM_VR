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
meetings_info = '/v1/query/meeting/' 
input_file = 'data/company_info.csv'         # To request meeting info from the company_info file
input_file_tickers = 'data/tickers_info.csv' # To request meeting info from the ticker_info file
output_file = 'data/meetings_info.csv'
failed_names = 'data/failed_meetings.csv'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/meetings_info_query.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_existing_data(output_file) -> pd.DataFrame:
        """Load existing meetings info data if available"""
        output_file = Path(output_file)
        if output_file.exists():
            try:
                existing_df = pd.read_csv(output_file)
                logger.info(f"Loaded existing data with {len(existing_df)} records")
                return existing_df
            except Exception as e:
                logger.warning(f"Failed to load existing data: {e}")
        return pd.DataFrame()

def should_scrape(meeting_id: str, existing_df: pd.DataFrame) -> bool:
        "Check if name needs to be queried"
        if existing_df.empty:
            return True
        # Check if name already exists
        mask = (existing_df['meetingId'] == meeting_id)
        return not mask.any()
           
def query_meetings_info(output_file):
    logger.info(f"Loading input file: {input_file_tickers}")
    input_df = pd.read_csv(input_file_tickers)
    logger.info(f"Total rows in input CSV: {len(input_df)}")

    # Load existing data if available
    existing_df = load_existing_data(output_file)

    # Process each name
    skipped_count = 0
    processed_count = 0
    failed_meetings = []

    for index, row in tqdm(input_df.iterrows(), total=len(input_df), desc="Processing info"):
        meeting_id = row.get('meetingId', '')
        
        processed_count += 1

        # Check if we need to scrape this name
        if not should_scrape(meeting_id, existing_df):
            skipped_count += 1
            logger.debug(f"Skipping {meeting_id} - already exists")
            continue

        # Query the company info
        meeting_info = pd.DataFrame()

        try:
            result = requests.get(url=f'{url}{meetings_info}{meeting_id}', headers=header)
            
            if result.status_code==429:
                logger.error("API rate limit exceeded (429) - stopping")
                break 

            if result.status_code != 200:
                logger.error(f"Request for {meeting_id} failed with status code {result.status_code}")
                failed_meetings.append(meeting_id)
                continue
            
            table_meeting = pd.DataFrame(json.loads(result.content))
            if table_meeting.status.iloc[0] == 'success':
                meeting_votes = pd.DataFrame(table_meeting.meeting['meetingVotes'])
                meeting_info.at[0, 'companyId'] = table_meeting.meeting['companyId']
                meeting_info.at[0,'companyName'] = table_meeting.meeting['companyName']
                meeting_info.at[0,'companyTicker'] = table_meeting.meeting['companyTicker']
                meeting_info.at[0,'isin'] = table_meeting.meeting['isin']
                meeting_info.at[0,'meetingDate'] = table_meeting.meeting['meetingDate']
                meeting_info.at[0,'meetingId'] = table_meeting.meeting['meetingId']
                meeting_info.at[0,'meetingType'] = table_meeting.meeting['meetingType']
                meeting_info = meeting_info.merge(meeting_votes, on='meetingId', how='outer')

                processed_count += 1

        except Exception as e:
            logger.error(f"Unexpected error for {meeting_id}: {e}")
            failed_meetings.append(meeting_id)
            continue

        try:
            # Append to existing file or create new one
            output_file = Path(output_file)
            if output_file.exists():
                meeting_info.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8')
            else:
                meeting_info.to_csv(output_file, index=False, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to save meetings data: {e}")

                
        # Update existing_df to avoid duplicates in current session
        existing_df = pd.concat([existing_df, meeting_info], ignore_index=True)
            
    logger.info("Scraping completed")
    logger.info(f"Total processed: {processed_count}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Failed: {len(failed_meetings)}, meetings ids saved to {failed_names}")
    
    if failed_meetings:
        failed_companies_df = pd.DataFrame(failed_meetings)
        failed_companies_df.to_csv(failed_names, mode='a', header=False, index=False, encoding='utf-8')

def main():
    logger.info("Starting info quering")
    query_meetings_info(output_file)

if __name__ == "__main__":
    main()