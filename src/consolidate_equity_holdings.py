import pandas as pd
import os
import glob
import re

def consolidate_equity_holdings(folder_path, output_file):
    """
    Consolidates equity holdings from multiple CSV files into a single file
    with dates as columns and (Region, Country, Name, Industry) as keys.
    """
    
    pattern = os.path.join(folder_path, 'eq_*.csv')
    csv_files = glob.glob(pattern)
    
    date_pattern = re.compile(r'eq_(\d{4})1231\.csv$')

    all_data = []
    for file_path in csv_files:
        match = date_pattern.search(os.path.basename(file_path))
        if not match:
            continue
            
        year = match.group(1) # The first parenthesized subgroup
        print(f"Reading {os.path.basename(file_path)}...")
        
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-16')
            
            # Keep only needed columns
            df = df[['Region', 'Country', 'Name', 'Industry', 'Ownership']].copy()
            
            # Clean Ownership column from '%' sign and convert to number
            df['Ownership'] = df['Ownership'].astype(str).str.replace('%', '').str.strip()
            df['Ownership'] = pd.to_numeric(df['Ownership'])
            
            # Add year column for future pivoting
            df['Year'] = year
            
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    if not all_data:
        print("No data files were successfully read.")
        return None
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Pivot the data: keys as rows, years as columns
    pivoted_df = combined_df.pivot_table(
        index=['Region', 'Country', 'Name', 'Industry'],
        columns='Year',
        values='Ownership',
        fill_value=0, # Value to replace missing values with
    )
    
    # Reset index to make keys regular columns
    pivoted_df = pivoted_df.reset_index()
    
    # Rename columns to have 'Ownership_' prefix
    pivoted_df.columns = ['Region', 'Country', 'Name', 'Industry'] + \
                         [f'Ownership_{col}' for col in pivoted_df.columns[4:]]
    
    pivoted_df = pivoted_df.sort_values(['Region', 'Country', 'Name', 'Industry'])
    
    pivoted_df.to_csv(output_file, index=False, sep=';', float_format='%.6f')
    
    print(f"Total unique holdings (keys): {len(pivoted_df)}")
    
    return pivoted_df

def main():
    FOLDER_PATH = 'equity_holdings'
    OUTPUT_FILE = 'data/consolidated_equity_holdings.csv'
    
    result = consolidate_equity_holdings(FOLDER_PATH, OUTPUT_FILE)
    
    if result is not None:
        print("\n--- Ownership Statistics per Year ---")
        year_columns = [col for col in result.columns if col.startswith('Ownership_')]
        for year_col in year_columns:
            non_zero = (result[year_col] > 0).sum()
            print(f"{year_col}: {non_zero} non-zero entries")

if __name__ == "__main__":
    main()