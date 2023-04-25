import openai
import pandas as pd
import json

summary_database = 'summary_database_vf.xlsx'

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey.txt')


def gpt3_embedding(content, engine='text-embedding-ada-002'):
    # encode to ASCII then decode to prevent chatgpt errors
    content = content.encode(encoding='ASCII', errors='ignore').decode()
    # generate embedding data for documents/questions/user input
    response = openai.Embedding.create(input=content, engine=engine)
    # creates a vector containing the embedding data
    vector = response['data'][0]['embedding']
    return vector

"""
1. Read the Excel database into pandas DataFrames
2. Make embeddings of each column into json index files: "GPT MS Summary","GPT CS Summary","GPT MS Keywords","GPT CS Keywords" columns, 
"""

df = pd.read_excel(summary_database)

columns = ["GPT MS Summary","GPT CS Summary","GPT MS Keywords","GPT CS Keywords"]

for column in columns:
    result = list()
    for index, row in df.iterrows():
        if not pd.isna(row[column]):
            embedding = gpt3_embedding(row[column].encode(encoding='ASCII',errors='ignore').decode())
            if column == 'GPT MS Summary' or column == 'GPT MS Keywords':
                info = {"index": index, "content": row[column], "json": row["GPT MS JSON"], "embedding": embedding}
            elif column == 'GPT CS Summary' or column == 'GPT CS Keywords':
                info = {"index": index, "content": row[column], "json": row["GPT CS JSON"], "embedding": embedding}
            result.append(info)

    with open(f"embedding_{column}.json", "w", encoding='utf-8') as outfile:
        json.dump(result, outfile, indent = 2)
        print (f"Embedding {column} done")