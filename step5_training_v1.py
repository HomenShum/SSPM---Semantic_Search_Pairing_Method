import pandas as pd
import json
import openai 

#Load OPENAI GPT
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey.txt')

def gpt3_embedding(content, engine='text-embedding-ada-002'):
    content = content.encode(encoding='ASCII',errors='ignore').decode()
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector

# Read the Excel file
filepath = r'Manual_Updated_Key_v1_with_ontology.xlsx'
df = pd.read_excel(filepath)

# Initialize an empty list to store the JSON data
json_data = list()

# Iterate through each row of the DataFrame
for index, row in df.iterrows():
    # Extract the contents of columns 0-4, 6-7 and concatenate them
    ms_json = str(row['MS JSON'])
    cs_json = str(row['CS JSON'])
    combined_json = 'Microsoft Alert JSON: ' + ms_json + 'CrowdStrike Alert JSON ' + cs_json

    # Extract the contents of column 9 (Summary)
    output = row['Common Ontology']
    # if NaN  
    if pd.isna(output):
        output = "Unknown"
    
    # Format the data into the specified JSON structure
    json_entry = {
        "Search Query": combined_json,
        "Vector": gpt3_embedding(combined_json),
        "Output": output
    }
    
    # Append the JSON entry to the json_data list
    json_data.append(json_entry)

# Save the JSON data to a file
with open('training_dataset_v1.json', 'w', encoding='utf-8') as outfile:
    json.dump(json_data, outfile, indent=2)

print("JSON file saved with search queries and outputs!")
