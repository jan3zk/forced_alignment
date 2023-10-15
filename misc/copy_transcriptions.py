import pandas as pd
import os
import glob

def main():
    # Get a list of all Excel files in the input directory
    inputDir = './xlsx/'
    excel_files = glob.glob(os.path.join(inputDir,'*.xlsx'))

    # Loop through each Excel file
    for excel_file in excel_files:
        # Read the Excel file
        df = pd.read_excel(excel_file)

        # Loop through each row in the dataframe
        for index, row in df.iterrows():
            # Get the file name and content
            file_name = row[0]
            if file_name != file_name or "NAVODILO" in file_name:
                continue
            content = row[1]

            # Replace the newline character with a space in the content
            content = content.replace('\n', ' ')
            content = content.replace('_x000D_', '')

            # Open the file and write the content
            with open(f'{file_name}.txt', 'w') as f:
                f.write(str(content))

if __name__ == "__main__":
    main()

