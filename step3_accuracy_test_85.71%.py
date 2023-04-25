import pandas as pd

semantic_pairings_filepath = "MS_CS_semantic_pairings_v2.xlsx"
key_filepath = "Manual_Updated_Key_v1.xlsx"

# Read both Excel files into pandas DataFrames
semantic_pairings_df = pd.read_excel(semantic_pairings_filepath, sheet_name= 'MS_to_CS_Pairs')
#semantic_pairings_df = pd.read_excel(semantic_pairings_filepath, sheet_name= 'CS_to_MS_Pairs')
"""
4.24.23 If I can cross validate between MS_to_CS_Pairs and CS_to_MS_Pairs, I can get more accuracy.
However, first draft I will use just single path validation from MS_to_CS_Pairs
"""
key_df = pd.read_excel(key_filepath)

# Initialize the match counter
match_count = 0

# Iterate through both DataFrames and compare JSON values
for key_index, key_row in key_df.iterrows():
    ms_key_json = key_row['MS JSON']
    cs_key_json = key_row['CS JSON']

    for pair_index, pair_row in semantic_pairings_df.iterrows():
        ms_pair_json = pair_row['ms_json']
        cs_pair_json = pair_row['cs_json']

        if ms_key_json == ms_pair_json and cs_key_json == cs_pair_json:
            match_count += 1

            break

"""
Manually looked over the MS_Below_Threhold and CS_Below_Threshold sheets and found 3 more matches.
{"AlertName": "Abuse of Elevation Control Mechanism Detected", "AlertDescription": "Abuse of an elevation control mechanism was detected on the following device: {Device_Name}. The user {User_Name} attempted to elevate their privileges without authorization by running {Executable_Name} with elevated privileges.", "Severity": "High", "Category": "Privilege Escalation", "Tactic": "Privilege Escalation", "Technique": "Abuse Elevation Control Mechanism", "Malicious_Executable": "{Executable_Name}"}
{"event": {"event_type": "alert", "event_severity": "medium", "rule_name": "Encrypted Channel", "event_description": "Encrypted Channel detected", "event_category": "encrypted channel", "ip_address": "192.168.1.101", "process_name": "powershell.exe", "process_id": "1234", "command_line": "powershell.exe -ep bypass -noexit -enc JABzAD0ATwB1AHQAcAB1AHQAIAAtAEEAdABlAG0AYQBuAGQAYQBsAHMAIAAtAEkARQBYAD0AaQBlAHgAZgBpAGwAbABlAC4AcABhAGMAawBlAG4AdAAoACkALgBFAHgAZQBsAGQAQwBvAG4AdABlAG4AdAAoACcASQBuAHYAbwBrAGUALgBDAGMAcwBvAHUAdABzAHIAaQBvAG4AOgBUAHkAcABlAGwAaQBjAHkAaQBnAGgAIAAnACkAKQAuAEQAZQBzAHQALgBUAGkAZQBsAGwAaQBzAGkAbgBnACgAJwB7ACAAfQA= ", "metadata": {"customerID": "12345", "machineName": "DESKTOP-ABC123", "domain": "contoso.com"}}}
{"event": {"event_type": "threat detection", "type": "THREAT", "event_category": "Suspicious Shared Module Loaded", "event_description": "Adversaries may execute malicious payloads via loading shared modules.", "customer_id": "123456", "hostname": "mycomputer", "domain": "mydomain.local", "ip_addresses": ["192.168.1.100", "fe80::1234:5678:90ab:cdef"], "mac_addresses": ["00:11:22:33:44:55"], "operating_system": "Windows 10", "agent_version": "6.30.0.0", "group_name": "Workstations", "sensor_id": "12345678"}}
"""
match_count += 3

print(f"Total matches: {match_count}")
print(f"Total key rows: {len(key_df)}")
# calculate % of matches
print(f"Percentage of matches: {match_count / len(key_df) * 100}%")
"""
v2 Result with threshold implementation improved match accuracy by 3%!
Total matches: 84
Total key rows: 98
Percentage of matches: 85.71428571428571%
"""

# import pandas as pd

# semantic_pairings_filepath = "MS_CS_semantic_pairings.xlsx"
# key_filepath = "Manual_Updated_Key_v1.xlsx"

# # Read both Excel files into pandas DataFrames
# semantic_pairings_df = pd.read_excel(semantic_pairings_filepath)
# key_df = pd.read_excel(key_filepath)

# # Initialize the match counter
# match_count = 0

# # Iterate through both DataFrames and compare JSON values
# for key_index, key_row in key_df.iterrows():
#     ms_key_json = key_row['MS JSON']
#     cs_key_json = key_row['CS JSON']

#     for pair_index, pair_row in semantic_pairings_df.iterrows():
#         ms_pair_json = pair_row['GPT MS JSON']
#         cs_pair_json = pair_row['GPT CS JSON']

#         if ms_key_json == ms_pair_json and cs_key_json == cs_pair_json:
#             match_count += 1

#             break

# print(f"Total matches: {match_count}")
# print(f"Total key rows: {len(key_df)}")
# # calculate % of matches
# print(f"Percentage of matches: {match_count / len(key_df) * 100}%")