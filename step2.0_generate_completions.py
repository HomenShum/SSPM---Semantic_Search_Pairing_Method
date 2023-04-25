import glob
import json
import pandas as pd
import re
from time import sleep
import openai
import tenacity
import xlsxwriter


json_files = glob.glob('All/*.json')

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey.txt')

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
    tokens=500, # Limit the output to 256 tokens so that the completion is not too wordy
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

def generate_gpt_completion(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract the values (answers) that are strings and concatenate them with a period and space
    content = '. '.join(extract_strings(data))

    prompt = f"Perform Extractive Text Summarization to state the cybersecurity alert name and Quote relevant key characteristics of the alert content, then generate a description of the following cybersecurity alert content:\n{content}\n Summarization should be a concise definition of the alert that can be applicable to any cybersecurity vendors; do not include user name, IP addresses, ID, non-alert information, specific account information, or file path information. The format should be as follows:\n\nAlert Name: <Name> . - \nKey Characteristics: <Keywords> . - \nCybersecurity Alert Description: <Description> \n<<END>>"


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

def generate_gpt_keywords(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract the values (answers) that are strings and concatenate them with a period and space
    content = '. '.join(extract_strings(data))

    prompt = f"Quote relevant key characteristics in a list from the following content:\n{content}\n>"

    retries = 3
    for attempt in range(retries):
        try:
            # Using GPT-3.5-turbo chat completion
            completion = gpt_completion(prompt)
            return completion
        except openai.error.APIError as e:
            if attempt < retries - 1:  # if this is not the last attempt
                print(f"APIError occurred: {e}. Retrying...")
                sleep(5)  # wait for 5 seconds before retrying
            else:
                raise

# def gpt3_embedding(content, engine='text-embedding-ada-002'):
#     # encode to ASCII then decode to prevent chatgpt errors
#     content = content.encode(encoding='ASCII', errors='ignore').decode()
#     # generate embedding data for documents/questions/user input
#     response = openai.Embedding.create(input=content, engine=engine)
#     # creates a vector containing the embedding data
#     vector = response['data'][0]['embedding']
#     return vector

def update_json_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    summary = generate_gpt_completion(json_file)
    # summary_embedding = gpt3_embedding(summary)
    keywords = generate_gpt_keywords(json_file)
    # keywords_embedding = gpt3_embedding(keywords)

    print(f"Updated GPT completion for {json_file}")
    print(f"GPT Summary: {summary}")
    print(f"GPT Keywords: {keywords}")
    print(f"\n")

    # return summary, summary_embedding, keywords, keywords_embedding
    return summary, keywords

# Process all JSON files and create Excel database
workbook = xlsxwriter.Workbook('summary_database_vf.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write(0, 0, 'GPT MS JSON')
worksheet.write(0, 1, 'GPT CS JSON')
worksheet.write(0, 2, 'GPT MS Summary')
worksheet.write(0, 3, 'GPT CS Summary')
# worksheet.write(0, 4, 'GPT MS Summary Embedding')
# worksheet.write(0, 5, 'GPT CS Summary Embedding')
worksheet.write(0, 4, 'GPT MS Keywords')
worksheet.write(0, 5, 'GPT CS Keywords')
# worksheet.write(0, 8, 'GPT MS Keywords Embedding')
# worksheet.write(0, 9, 'GPT CS Keywords Embedding')

position = 0
for json_file in json_files:
    position += 1
    # summary, summary_embedding, keywords, keywords_embedding = update_json_file(json_file)
    summary, keywords = update_json_file(json_file)
    with open(json_file, 'r') as f:
        data = json.load(f)
    if json_file.endswith("MS.json"):
        worksheet.write(position, 0, json.dumps(data))
        worksheet.write(position, 2, summary)
        # worksheet.write(position, 4, str(summary_embedding))
        worksheet.write(position, 4, keywords)
        # worksheet.write(position, 8, str(keywords_embedding))
    elif json_file.endswith("CS.json"):
        worksheet.write(position, 1, json.dumps(data))
        worksheet.write(position, 3, summary)
        # worksheet.write(position, 5, str(summary_embedding))
        worksheet.write(position, 5, keywords)
        # worksheet.write(position, 9, str(keywords_embedding))

workbook.close()
print("JSON files updated with GPT completions!")
print("Excel database created.")
