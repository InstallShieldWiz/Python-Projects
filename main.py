######################################################################
#David Jacobson
# Description - This is program i designed using AI to suplement my coding to 
# convert information from a PDF to a csv file
# to be imported into an excel.  Namely taking bank statements and converting the 
# information within into a text file and
# then converting the text file using the "parse_transactions program to create a csv file for tax purposes."
#######################################################################


import pdfplumber
import pandas as pd
import re
import os

def pdf_to_csv(pdf_path, csv_path):
    # Create an empty list to store the rows
    formatted_data = []
    
    # Regular expression to match valid transaction lines
    transaction_pattern = re.compile(r'^\d{2}/\d{2} .*?(\$[\d,]+\.\d{2})')

    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through each page
        for page in pdf.pages:
            # Extract text from the page
            text = page.extract_text()
            if text:
                # Print the extracted text for debugging
                print("Extracted Text:\n", text)  
                
                # Split the text into lines
                lines = text.split('\n')
                
                # Process each line
                for i, line in enumerate(lines):
                    # Check if the line matches the transaction pattern
                    if transaction_pattern.match(line):
                        # Clean and format the line
                        formatted_data.append(line.strip())
                        
                        # Capture any additional lines that follow until the next date
                        for j in range(i + 1, len(lines)):
                            # Check if the next line starts with a date
                            if re.match(r'^\d{2}/\d{2}', lines[j]):
                                break  # Stop if we reach the next transaction line
                            # Otherwise, add the additional line
                            formatted_data.append(lines[j].strip())

    # Debugging: Print the formatted data
    print("Formatted Data:\n", formatted_data)

    # Create a DataFrame from the formatted data
    if formatted_data:  # Check if data is not empty
        df = pd.DataFrame(formatted_data)  # Create DataFrame without specifying headers
        # Save the DataFrame to a CSV file, ensuring comma separation
        df.to_csv(csv_path, index=False, header=False)  # Set header=False to avoid writing column names
        print(f"Data successfully written to {csv_path}.")  # Confirmation message
    else:
        print("No transaction data found in the PDF.")  # Debugging: Notify if no data is found

# Process all PDF files in the current directory
def process_all_pdfs():
    # Get a list of all PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    # Process each PDF file
    for pdf_file in pdf_files:
        csv_file = pdf_file.replace('.pdf', '.csv')  # Create a corresponding CSV file name
        print(f"Processing {pdf_file}...")
        pdf_to_csv(pdf_file, csv_file)

# Example usage
process_all_pdfs()