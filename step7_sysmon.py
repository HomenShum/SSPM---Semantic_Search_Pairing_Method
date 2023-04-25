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
    print (max_similarity)

    return closest_entry


# For those that are unknown, generate the keywords and summaries using the extract_string 

from time import sleep
import tenacity
import re

@tenacity.retry(
    stop=tenacity.stop_after_delay(30),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=30),
    retry=(tenacity.retry_if_exception_type(openai.error.APIError) |
           tenacity.retry_if_exception_type(openai.error.RateLimitError)),
    reraise=True,
)
def gpt_completion(
    prompt,
    engine="gpt-3.5-turbo",
    temp=0, # set at 0 to ensure consistent completion, increase accuracy along with UUID
    top_p=1.0,
    tokens=500, 
    freq_pen=0.25,
    pres_pen=0.0,
    stop=["<<END>>"],
):
    prompt = prompt.encode(encoding="ASCII", errors="ignore").decode()
    response = openai.ChatCompletion.create(
        model=engine,
        messages=[
            {"role": "system", "content": "Your task is to perform extractive summarization from JSON data to string context."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=tokens,
        temperature=temp,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop,
    )
    text = response["choices"][0]["message"]["content"].strip()
    text = re.sub("\s+", " ", text)
    return text

def extract_strings(data):
    result = []
    for value in data.values():
        if isinstance(value, str):
            result.append(value)
        elif isinstance(value, dict):
            result.extend(extract_strings(value))
    return result

def generate_gpt_completion(data):

    prompt = f"Perform Extractive Text Summarization to state the cybersecurity alert name and Quote relevant key characteristics of the alert content, then generate a description of the following cybersecurity alert content:\n{data}\n Summarization should be a concise definition of the alert that can be applicable to any cybersecurity vendors; do not include user name, IP addresses, ID, non-alert information, specific account information, or file path information. The format should be as follows:\n\nAlert Name: <Name> . - \nKey Characteristics: <Keywords> . - \nCybersecurity Alert Description: <Description> \n<<END>>"


    retries = 3
    for attempt in range(retries):
        try:
            completion = gpt_completion(prompt)  # Using GPT-3.5-turbo chat completion
            return completion
        except openai.error.APIError as e:
            if attempt < retries - 1:  # if this is not the last attempt
                print(f"APIError occurred: {e}. Retrying...")
                sleep(5)  # wait for 5 seconds before retrying
            else:
                raise

json_file = 'Archive\sysmon_all.json'

cs_summaries = read_json_file("embedding_GPT CS Summary.json")
ms_summaries = read_json_file("embedding_GPT MS Summary.json")

count = 0

for line in open(json_file, 'r', encoding='utf-8'):
    # print(line)
    closest_entry = find_closest_embedding(test_embedding(line), training_dataset)
    if closest_entry['Output'] == "Unknown":
        common_ontology = generate_gpt_completion(line)
    else:
        common_ontology = closest_entry['Output']
        count +=1
        print("common_ontology: ", common_ontology)
    
    # save the line + common_ontology in the format "line": "common_ontology"
    with open('Archive/sysmon_with_output.json', 'a') as f:
        f.write(json.dumps({line: common_ontology}) + '\n')
        

# Time result
print("--- %s seconds ---" % (time.time() - start_time))
print("count: ", count, "out of 28", "percentage via semantic search pairing: ", count/28*100, "%")

