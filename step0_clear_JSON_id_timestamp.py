# Loop through all of the JSON dictionaries to find timestamp and ID, then remove them from the dictionary
# This is to make the JSON files smaller and easier to work with

import json
import glob

def remove_irrelevant_items(data):
    irrelevant_keys = ['AlertID', 'AlertTimestamp', 'Affected_Device', 'Affected_User', 'event_id', 'event_timestamp', 'event_time', 'endpoint_id', 'host', 'Hostname', 'IP', 'OS', 'User', 'destination_port', 'destination_ip']

    if isinstance(data, dict):
        for key in irrelevant_keys:
            if key in data:
                del data[key]
            elif 'event' in data and key in data['event']:
                del data['event'][key]

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = remove_irrelevant_items(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        value[i] = remove_irrelevant_items(value[i])

    return data

# Search for JSON files and process them
json_files = glob.glob('All/*.json')

# Loop through each JSON file
for file_path in json_files:
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    # Remove irrelevant items
    data = remove_irrelevant_items(data)

    # Write the updated JSON data to the file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)
