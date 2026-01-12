import argparse
import logging
import sys
import pandas as pd
import glob
import os


def process_gas_data_file(template, file_path):
    '''
    Process a single gas data file according to the specified template.

    Args:
        template (int): Template id (1 for xlsx, 2 for csv).
        file_path (str): Path to the input file.

    Returns:
        pd.DataFrame: Processed dataframe with `date`, `day`, `month`, `year`, and `value`.
    '''
    if template == 1:
        # Read the CSV file into a DataFrame
        df = pd.read_excel(file_path)

        # Print head of dataframe in verbose mode
        logging.debug('Dataframe head:\n%s', df.head())

        # Rename columns to standard names
        df.rename(columns={df.columns[0]:"date_time", 
                           df.columns[1]:"value"}, 
                    inplace=True)

        # Split by comma first to separate Date from Times
        df[['date', 'time_slot']] = df['date_time'].str.split(', ', expand=True)

        # Split the Times column by the dash
        df[['start_time', 'end_time']] = df['time_slot'].str.split(' - ', expand=True)

        # Convert 'date' column to date format
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')

        # Change the date to date-1 when the start_time is between 00:00 and 06:00 hours
        df.loc[df['start_time'].str.slice(0, 2).astype(int) < 6, 'date'] = df['date'] - pd.Timedelta(days=1)

        # Create separate day, month, year columns from 'date'
        df['day'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year 

        # Clean up temporary column
        df = df.drop(columns=['time_slot'])

    elif template == 2:
        # Read the CSV file into a DataFrame with semicolon delimiter
        df = pd.read_csv(file_path, delimiter=';')
        
        # Print head of dataframe in verbose mode
        logging.debug('Dataframe head:\n%s', df.head())

        # Rename columns to standard names
        df.rename(columns={df.columns[1]:"date_time", 
                           df.columns[2]:"value"}, 
                    inplace=True)

        # Convert 'date_time' column to datetime format
        df['date_time'] = pd.to_datetime(df['date_time'], format='%d-%m-%Y %H:%M')

        # Create separate date and time columns
        df['date'] = df['date_time'].dt.date
        df['time'] = df['date_time'].dt.time

        # Change the date to date-1 when the end time is between 00:00 and 06:00 hours
        df.loc[df['date_time'].dt.hour <= 6, 'date'] = pd.to_datetime(df['date']) - pd.Timedelta(days=1)

        # Create separate day, month, year columns from 'date'
        df['day'] = pd.to_datetime(df['date']).dt.day
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['year'] = pd.to_datetime(df['date']).dt.year

        # Convert the value column from m3 to mWh (1 m3 = 10.55 kWh)
        df['value'] = df['value'] * 0.01055 

    # Return the processed DataFrame
    return df
  
def main():
    parser = argparse.ArgumentParser(description='Batch process gas usage files and produce monthly totals.')
    parser.add_argument('--source', '-s', default='./', help='Source folder to scan for .xlsx/.csv files (default: ./)')
    parser.add_argument('--output', '-o', default='./output/', help='Output folder for results (default: ./output/)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose (debug) logging')
    parser.epilog = 'This script scans a folder for .xlsx and .csv files, normalises gas consumption records, and writes monthly totals and details into an output folder.'
    
    # Parse arguments
    args = parser.parse_args() 

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')

    source_folder = args.source
    output_folder = args.output

    os.makedirs(output_folder, exist_ok=True)

    data_files = glob.glob(os.path.join(source_folder, '*.xlsx'))
    data_files += glob.glob(os.path.join(source_folder, '*.csv'))

    logging.info('Found %d files to process.', len(data_files))

    for file_path in data_files:
        try:
            # --- READ ---
            file_name = os.path.basename(file_path)
            logging.info('Processing: %s', file_name)

            # Get base name without extension
            base_name, _ = os.path.splitext(file_name)

            # Determine template based on file extension and process
            if file_path.endswith('.xlsx'):
                df = process_gas_data_file(template=1, file_path=file_path)
            elif file_path.endswith('.csv'):
                df = process_gas_data_file(template=2, file_path=file_path)
            else:
                logging.info(' -> Skipping unsupported file type: %s', file_name)
                continue

            # --- TRANSFORM & AGGREGATE ---
            # Create a new dataframe with monthly totals for each year
            aggregated_df = df.groupby(['year', 'month'])['value'].sum().reset_index()

            # --- WRITE ---
            # Create a new file_names for totals and details
            totals_file_name = f"{base_name}_monthly_totals.xlsx"
            details_file_name = f"{base_name}_details.xlsx"
            totals_save_path = os.path.join(output_folder, totals_file_name)
            details_save_path = os.path.join(output_folder, details_file_name)

            # Write to Excel files
            aggregated_df.to_excel(totals_save_path, index=False)
            df.to_excel(details_save_path, index=False)

            logging.debug('Wrote totals to %s and details to %s', totals_save_path, details_save_path)

        except Exception:
            logging.exception('Error processing %s', file_path)

    logging.info('Batch processing complete.')

if __name__ == '__main__':
    main()
