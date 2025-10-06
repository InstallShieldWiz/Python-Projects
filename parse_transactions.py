######################################################################
#David Jacobson
# Description - This is program i designed using AI to suplement my coding to 
# convert information from a PDF to a csv file
# to be imported into an excel.  Namely taking bank statements and converting the 
# information within into a text file and
# then converting the text file using the "parse_transactions program to create a csv file for tax purposes."
#######################################################################


import pandas as pd
import re
import os

def clean_and_parse_text(input_file):
    # Create a list to hold the parsed transaction data
    parsed_data = []

    # Regular expression to match valid transaction lines
    transaction_pattern = re.compile(
        r'^(?P<date>\d{2}/\d{2}) (?P<description>.+?) (?P<debits>\$[\d,]*\.?\d{0,2}|0) (?P<credits>\$[\d,]*\.?\d{0,2}|0) (?P<balance>\$[\d,]*\.?\d{0,2})'
    )

    # Read the input text file
    with open(input_file, 'r') as file:
        lines = file.readlines()
        
        # Process each line
        for i in range(len(lines)):
            line = lines[i].replace('"', '').strip()  # Remove quotation marks and strip whitespace
            print(f"Processing line: {line}")  # Debugging output
            
            # Match the line against the transaction pattern
            match = transaction_pattern.match(line)
            if match:
                # Start building the transaction data
                transaction_data = match.groupdict()
                additional_info = []

                # Capture any additional lines that follow until the next date
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].replace('"', '').strip()  # Clean the next line
                    if re.match(r'^\d{2}/\d{2}', next_line):  # Check if the next line starts with a date
                        break  # Stop if we reach the next transaction line
                    additional_info.append(next_line)  # Add the additional line

                # Combine additional information into a single string
                transaction_data['additional_info'] = ' '.join(additional_info)
                parsed_data.append(transaction_data)

    return parsed_data  # Return the parsed data

# Process all CSV files in the current directory and compile into a single CSV
def process_all_csvs(output_file):
    all_parsed_data = []  # List to hold all parsed data from all files

    # Get a list of all CSV files in the current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        parsed_data = clean_and_parse_text(csv_file)  # Get parsed data from the current file
        all_parsed_data.extend(parsed_data)  # Add to the overall list

    # Create a DataFrame from all parsed data
    if all_parsed_data:
        # Create DataFrame and handle additional info
        df = pd.DataFrame(all_parsed_data)
        # Save the DataFrame to a single CSV file
        df.to_csv(output_file, index=False)
        print(f"Data successfully written to {output_file}.")
    else:
        print("No valid transaction data found in the input files.")

# Example usage
output_file = 'compiled_transactions.csv'  # Desired output CSV file path
process_all_csvs(output_file)