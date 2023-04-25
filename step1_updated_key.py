import glob
import json
import pandas as pd
import re

# Read excel file
df = pd.read_excel('Key.xlsx')

# Create new columns for MS JSON and CS JSON
df['MS JSON'] = ''
df['CS JSON'] = ''

# Function to recursively search JSON data
def recursive_search(data, search_str):
    result = []

    search_words = re.findall(r'\b\w+\b', search_str)
    search_pattern = re.compile(r'\b(?:' + '|'.join(search_words) + r')\b', re.IGNORECASE)

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result.extend(recursive_search(value, search_str))
            elif isinstance(value, str) and search_pattern.search(value):
                result.append(value)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result.extend(recursive_search(item, search_str))
            elif isinstance(item, str) and search_pattern.search(item):
                result.append(item)

    return result


# Iterate over each row
for index, row in df.iterrows():
    ms_content = str(row['Microsoft'])
    cs_content = str(row['CrowdStrike']) # Convert to string

    # Find JSON files
    json_files = glob.glob('All/*.json')
    for file in json_files:
        try:
            if file.endswith('MS.json'):
                with open(file, 'r') as f:
                    data = json.load(f)
                    if ms_content in recursive_search(data, ms_content):
                        df.at[index, 'MS JSON'] = json.dumps(data)
            elif file.endswith('CS.json'):
                with open(file, 'r') as f:
                    data = json.load(f)
                    if cs_content in recursive_search(data, cs_content):
                        df.at[index, 'CS JSON'] = json.dumps(data)
        except Exception as e:
            print(f"Error processing file '{file}': {e}")

# Save updated dataframe to a new excel file
df.to_excel('Updated_Key_v1.xlsx', index=False)

### Once this is complete, we will have to manually update 30 cells of the excel file with the correct JSON data
### Then the Manual_Updated_Key_v1.xlsx file will be used for accuracy testing in step 3
### The excel file will also be used for testing the semantic search pairing method