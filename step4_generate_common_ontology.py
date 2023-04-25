import pandas as pd
import openai
from time import sleep
import re
import tenacity

semantic_pairings_filepath = "MS_CS_semantic_pairings_v2.xlsx"
key_filepath = "Manual_Updated_Key_v1.xlsx"


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
    temp=0,  # set at 0 to ensure consistent completion, increase accuracy along with UUID
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
            {"role": "system", "content": "Your task is to perform Abstractive Text Summarization on cybersecurity alerts from different vendors."},
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


def summarize_gpt_completion(content):
    prompt = f"Perform Abstractive Text Summarization to state the cybersecurity alert name and Quote relevant key characteristics of the alert content, then generate a description of the following cybersecurity alert content:\n{content}\n Summarization should be a concise definition of the alert that can be applicable to any cybersecurity vendors; do not include user name, IP addresses, ID, non-alert information, specific account information, or file path information. The format should be as follows:\n\nAlert Name: <Name> . - \nKey Characteristics: <Keywords> . - \nCybersecurity Alert Description: <Description> \n<<END>>"

    retries = 3
    for attempt in range(retries):
        try:
            # Using GPT-3.5-turbo chat completion
            summary = gpt_completion(prompt)
            print(summary + "\n")
            return summary
        except openai.error.APIError as e:
            if attempt < retries - 1:  # if this is not the last attempt
                print(f"APIError occurred: {e}. Retrying...")
                sleep(5)  # wait for 5 seconds before retrying
            else:
                raise


# Read both Excel files into pandas DataFrames
semantic_pairings_df = pd.read_excel(
    semantic_pairings_filepath, sheet_name='MS_to_CS_Pairs')
key_df = pd.read_excel(key_filepath)

# Add the "Common Ontology" column to key_df
key_df["Common Ontology"] = ""

# Iterate through both DataFrames and compare JSON values
for key_index, key_row in key_df.iterrows():
    ms_key_json = key_row['MS JSON']
    cs_key_json = key_row['CS JSON']

    for pair_index, pair_row in semantic_pairings_df.iterrows():
        ms_pair_json = pair_row['ms_json']
        cs_pair_json = pair_row['cs_json']

        if ms_key_json == ms_pair_json and cs_key_json == cs_pair_json:
            # Concatenate ms_content and cs_content
            content = str(pair_row['ms_content']) + \
                ' ' + str(pair_row['cs_content'])

            # Generate summary using summarize_gpt_completion
            summary = summarize_gpt_completion(content)

            # Add the summary to the corresponding row in key_df
            key_df.at[key_index, "Common Ontology"] = summary

            break

# Save the updated DataFrame to a new Excel file
key_df.to_excel("Manual_Updated_Key_v1_with_ontology.xlsx", index=False)
