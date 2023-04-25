"""
The semantic search pairing model uses the following vector database: 
    training_dataset_v1.json
    embedding_GPT MS Summaries
    embedding_GPT CS Summaries

1. Test alert data is read from the file, each line of alert json is stripped and loaded into "all_data" list
2. For each alert, it is loaded into embedding function and compared to training_dataset_v1.json
3. The closest match is found and the alert is paired with the closest match
4. ELSE: The model outputs "Unknown" = It was not able to classify the alert because the alert was not in the training dataset
5. The alert will then be paired with the closest match in the combined embedding_GPT Summaries vector database
    - However, in preparation for production ready environment, I prepared the summary generation for the unknown alerts 
    - The summary generation is commented out for now, but can be uncommented if needed
    - In order to classify whether or not the alert is unknown to existing training dataset, use cosine similarity threshold
    - - Obeserve the cosine similarity threshold for the JSON that outputs Unknown when compared to the training dataset that does not have the pairings ready to output "Unknown"
    - - Write the minimum threshold for the cosine similarity and use that as the threshold for the model 

Why it works?
The accuracy of the semantic pairing method was at 85.71%.
This accuracy is important because it determines how the next portion - semantic search pairing method - would perform.
    The alert's json data structure differ in IP, ID, and timestamp related information
    The semantic structure and contextual meaning that identifies each alert does not change.  
    Therefore, Semantic search became very handy: it allows small training dataset, and with the right structuring, we can perform semantic search to very quickly determine the common ontology. 

Accuracy is secured, next, semantic search pairing method:
    The corresponding JSON pairs is concatenated and written into training_dataset_v1.json
    The embeddings are then generated for the training_dataset_v1.json
    The corresponding common ontology output is also written into th training_dataset_v1.json
With this vector database, we can now perform semantic search pairing method to quickly determine the common ontology of the alert.

Time that it took to process 100 alerts from CS-MS-Test-Data = 83.82 Seconds

Post-hackathon reflections:
This entire trial run result demonstrates the power of NLP tool when combined with an optimized vector database management system. 
The size of the training data is very small. Yet, the accuracy of the semantic pairing method is very high and the search speed is very fast.
It just takes a long time to iterate the prompt and the semantic search pairing method and database organization/extraction method for it to work correctly.
The semantic search pairing method is very powerful and can be used for many different applications. 
"""

import openai
import json
import numpy as np

# Add function to calculate time that it took to run the program
import time
start_time = time.time()

# Load OPENAI GPT


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey.txt')


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def gpt3_embedding(content, engine='text-embedding-ada-002'):
    content = content.encode(encoding='ASCII', errors='ignore').decode()
    response = openai.Embedding.create(input=content, engine=engine)
    vector = response['data'][0]['embedding']
    return vector


filepath = 'training_dataset_v1.json'


def load_training_dataset(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


training_dataset = load_training_dataset(filepath)


def test_embedding(input):
    return gpt3_embedding(json.dumps(input))


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def find_closest_embedding(embedding, training_dataset):
    max_similarity = float('-inf')
    closest_entry = None

    for entry in training_dataset:
        if 'Vector' in entry and entry['Vector'] is not None:
            vector = np.array(entry['Vector'])
        elif 'embedding' in entry:
            vector = np.array(entry['embedding'])
        similarity = cosine_similarity(embedding, vector)

        if similarity > max_similarity:
            max_similarity = similarity
            closest_entry = entry

    return closest_entry


# Now do it for CS-MS-Test-Data.json
json_file = 'CS-MS-Test-Data.json'
cs_summaries = read_json_file("embedding_GPT CS Summary.json")
ms_summaries = read_json_file("embedding_GPT MS Summary.json")

# combine the two
combined_summaries = cs_summaries + ms_summaries

with open(json_file, 'r') as f:
    all_data = []
    for line in f:
        data = json.loads(line.strip())
        all_data.append(data)

# Process all_data as needed
for dictionary in all_data[:10]:
    embedding = test_embedding(dictionary)
    closest_entry = find_closest_embedding(embedding, training_dataset)
    if closest_entry['Output'] == "Unknown":
        closest_sum_entry = find_closest_embedding(
            embedding, combined_summaries)
        dictionary['Output'] = closest_sum_entry['content']
    else:
        dictionary['Output'] = closest_entry['Output']

# Save the dictionary
with open('CS-MS-Test-Data_with_output.json', 'w') as f:
    for entry in all_data:
        f.write(json.dumps(entry) + '\n')

# time result
print("--- %s seconds ---" % (time.time() - start_time))

"""
json_file = 'All-CS\All-CS.json'
cs_summaries = read_json_file("embedding_GPT CS Summary.json")

with open(json_file, 'r') as f:
    all_data = []
    for line in f:
        data = json.loads(line.strip())
        all_data.append(data)

# test_json = list()

# Process all_data as needed
for dictionary in all_data[:10]:
    embedding = test_embedding(dictionary)
    closest_entry = find_closest_embedding(embedding, training_dataset)
    if closest_entry['Output'] == "Unknown":
        #use embedding to find the closest to all of cs_summaries['embedding']
        #append the cs_summaries['content'] to the dictionary['Output']
        for cs_summary in cs_summaries:
            cs_embedding = cs_summary['embedding']
            closest_cs_entry = find_closest_embedding(cs_embedding, training_dataset)
            dictionary['Output'] = closest_cs_entry['Output']
    else:
        dictionary['Output'] = closest_entry['Output']
#         # For those that are not Unknown, we can save a list of test_json with the "Search Query" from the training_dataset
#         test_json.append(closest_entry['Search Query'])

# print (test_json)
    ################################################################
    # Uncomment the following lines to generate summaries for those that are Unknown
    # However, since we already have pregenerated summaries from embedding_GPT CS Summary and embedding_GPT MS Summary json files, we use the embedding of the test json content to search through those json files and append the "content" to the dictionary['Output']
    # In the future, in the case that there is unknown alerts that have not been summarized, this can be used to generate summary, then we can work on appending it to the alert datasets
    ################################################################

    # if closest_entry['Output'] == "Unknown":
    #     summary = generate_gpt_completion(dictionary)
    #     dictionary['Output'] = summary
    # else:
    #     dictionary['Output'] = closest_entry['Output']

# Save the updated all_data to a new file
with open('All-CS\All-CS_with_output.json', 'w') as f:
    for entry in all_data:
        f.write(json.dumps(entry) + '\n')

# Now do it for All-MS.json
json_file = 'All-MS\All-MS.json'
ms_summaries = read_json_file("embedding_GPT MS Summary.json")

with open(json_file, 'r') as f:
    all_data = []
    for line in f:
        data = json.loads(line.strip())
        all_data.append(data)

# Process all_data as needed
for dictionary in all_data[:10]:
    embedding = test_embedding(dictionary)
    closest_entry = find_closest_embedding(embedding, training_dataset)
    if closest_entry['Output'] == "Unknown":
        #use embedding to find the closest to all of ms_summaries['embedding']
        #append the ms_summaries['content'] to the dictionary['Output']
        for ms_summary in ms_summaries:
            ms_embedding = ms_summary['embedding']
            closest_ms_entry = find_closest_embedding(ms_embedding, training_dataset)
            dictionary['Output'] = closest_ms_entry['Output']
    else:
        dictionary['Output'] = closest_entry['Output']
        test_json.append(closest_entry['Search Query'])

# Save the dictionary
with open('All-MS\All-MS_with_output.json', 'w') as f:
    for entry in all_data:
        f.write(json.dumps(entry) + '\n')
"""


"""
closest_entry = find_closest_embedding(test_embedding(test), training_dataset)
print(closest_entry['Output'])
# Container Administration Command Execution Detected
closest_entry = find_closest_embedding(test_embedding(test1), training_dataset)
print(closest_entry['Output'])
# Unknown
"""

"""
For those that are unknown, generate the keywords and summaries using the extract_string 

# from time import sleep
# import tenacity
# import re

# @tenacity.retry(
#     stop=tenacity.stop_after_delay(30),
#     wait=tenacity.wait_exponential(multiplier=1, min=1, max=30),
#     retry=(tenacity.retry_if_exception_type(openai.error.APIError) |
#            tenacity.retry_if_exception_type(openai.error.RateLimitError)),
#     reraise=True,
# )
# def gpt_completion(
#     prompt,
#     engine="gpt-3.5-turbo",
#     temp=0, # set at 0 to ensure consistent completion, increase accuracy along with UUID
#     top_p=1.0,
#     tokens=500, # Limit the output to 256 tokens so that the completion is not too wordy
#     freq_pen=0.25,
#     pres_pen=0.0,
#     stop=["<<END>>"],
# ):
#     prompt = prompt.encode(encoding="ASCII", errors="ignore").decode()
#     response = openai.ChatCompletion.create(
#         model=engine,
#         messages=[
#             {"role": "system", "content": "Your task is to perform extractive summarization from JSON data to string context."},
#             {"role": "user", "content": prompt},
#         ],
#         max_tokens=tokens,
#         temperature=temp,
#         top_p=top_p,
#         frequency_penalty=freq_pen,
#         presence_penalty=pres_pen,
#         stop=stop,
#     )
#     text = response["choices"][0]["message"]["content"].strip()
#     text = re.sub("\s+", " ", text)
#     return text

# def extract_strings(data):
#     result = []
#     for value in data.values():
#         if isinstance(value, str):
#             result.append(value)
#         elif isinstance(value, dict):
#             result.extend(extract_strings(value))
#     return result

# def generate_gpt_completion(json_file):
#     with open(json_file, 'r') as f:
#         data = json.load(f)

#     # Extract the values (answers) that are strings and concatenate them with a period and space
#     content = '. '.join(extract_strings(data))

#     prompt = f"Perform Extractive Text Summarization to state the cybersecurity alert name and Quote relevant key characteristics of the alert content, then generate a description of the following cybersecurity alert content:\n{content}\n Summarization should be a concise definition of the alert that can be applicable to any cybersecurity vendors; do not include user name, IP addresses, ID, non-alert information, specific account information, or file path information. The format should be as follows:\n\nAlert Name: <Name> . - \nKey Characteristics: <Keywords> . - \nCybersecurity Alert Description: <Description> \n<<END>>"


#     retries = 3
#     for attempt in range(retries):
#         try:
#             completion = gpt_completion(prompt)  # Using GPT-3.5-turbo chat completion
#             return completion
#         except openai.error.APIError as e:
#             if attempt < retries - 1:  # if this is not the last attempt
#                 print(f"APIError occurred: {e}. Retrying...")
#                 sleep(5)  # wait for 5 seconds before retrying
#             else:
#                 raise

"""
