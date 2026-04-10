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
comp_info = '/v1/query/company/' # Company meetings
input_file = 'data/company_names.csv'
output_file = 'data/company_info.csv'
failed_names = 'data/failed_names.csv'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/company_info_query.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_existing_data(output_file) -> pd.DataFrame:
        """Load existing company info data if available"""
        output_file = Path(output_file)
        if output_file.exists():
            try:
                existing_df = pd.read_csv(output_file)
                logger.info(f"Loaded existing data with {len(existing_df)} records")
                return existing_df
            except Exception as e:
                logger.warning(f"Failed to load existing data: {e}")
        return pd.DataFrame()

def should_scrape(company_name: str, existing_df: pd.DataFrame) -> bool:
        "Check if name needs to be queried"
        if existing_df.empty:
            return True
        # Check if name already exists
        mask = (existing_df['name'] == company_name)
        return not mask.any()
           
def query_company_info(output_file):
    logger.info(f"Loading input file: {input_file}")
    input_df = pd.read_csv(input_file)
    logger.info(f"Total rows in input CSV: {len(input_df)}")

    # Load existing data if available
    existing_df = load_existing_data(output_file)

    # Process each name
    skipped_count = 0
    processed_count = 0
    failed_companies = []

    for index, row in tqdm(input_df.iterrows(), total=len(input_df), desc="Processing companies info"):
        company_name = row.get('name', '')
        
        processed_count += 1

        # Check if we need to scrape this name
        if not should_scrape(company_name, existing_df):
            skipped_count += 1
            logger.debug(f"Skipping {company_name} - already exists with same date")
            continue

        # Query the company info
        all_company_rows = []

        try:
            result = requests.get(url=f'{url}{comp_info}{company_name}', headers=header)
            
            if result.status_code==429:
                logger.error("API rate limit exceeded (429) - stopping")
                break 

            if result.status_code != 200:
                logger.error(f"Request for {company_name} failed with status code {result.status_code}")
                failed_companies.append(company_name)
                continue
            
            data = pd.DataFrame(json.loads(result.content))
            if data.status[0] == 'success':
                company_data = data.companies[0]            
                meetings_data = company_data.get('meetings', [])
                for meeting in meetings_data:
                    row = {
                        'company': company_name,
                        'name': company_data.get('name') if company_data else "",
                        'country': company_data.get('country') if company_data else "",
                        'ticker': company_data.get('Ticker') if company_data else "",
                        'id': company_data.get('id') if company_data else "",
                        'isin': company_data.get('isin') if company_data else "", 
                        'meetingDate': meeting.get('meetingDate') if meeting else "",
                        'meetingId': meeting.get('meetingId') if meeting else "",
                        'meetingType': meeting.get('meetingType')if meeting else ""
                    }
                    all_company_rows.append(row)
                processed_count += 1

            elif data.empty and not 'companies':
                failed_companies.append(company_name)
                logger.warning(f"No company data found for: {company_name}")
                
            elif data.message.messageString == 'LimitExceeded':
                failed_companies.append(company_name)
                logger.error("API limit exceeded")
                break

        except Exception as e:
            logger.error(f"Unexpected error for {company_name}: {e}")
            failed_companies.append(company_name)
            continue

        try:
            df = pd.DataFrame(all_company_rows)
            # Append to existing file or create new one
            output_file = Path(output_file)
            if output_file.exists():
                df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8')
            else:
                df.to_csv(output_file, index=False, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to save product data: {e}")

                
        # Update existing_df to avoid duplicates in current session
        existing_df = pd.concat([existing_df, pd.DataFrame(all_company_rows)], ignore_index=True)
            
    logger.info("Scraping completed")
    logger.info(f"Total processed: {processed_count}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Failed: {len(failed_companies)}, company names saved to {failed_names}")
    
    if failed_companies:
        failed_companies_df = pd.DataFrame(failed_companies)
        failed_companies_df.to_csv(failed_names, mode='a', header=False, index=False, encoding='utf-8')

def main():
    logger.info("Starting companies info quering")
    query_company_info(output_file)

if __name__ == "__main__":
    main()