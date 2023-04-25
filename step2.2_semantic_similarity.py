import json
import numpy as np
import pandas as pd


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def find_most_similar_pair(embeddings_ms, embeddings_cs, embeddings_ms_keywords, embeddings_cs_keywords, threshold):
    most_similar_pairs = []
    below_threshold = []

    for ms, ms_kw in zip(embeddings_ms, embeddings_ms_keywords):
        highest_similarity = 0
        most_similar_cs = None

        for cs, cs_kw in zip(embeddings_cs, embeddings_cs_keywords):
            summary_similarity = np.dot(ms["embedding"], cs["embedding"]) / (
                np.linalg.norm(ms["embedding"]) * np.linalg.norm(cs["embedding"]))
            keyword_similarity = np.dot(ms_kw["embedding"], cs_kw["embedding"]) / (
                np.linalg.norm(ms_kw["embedding"]) * np.linalg.norm(cs_kw["embedding"]))
            similarity = (summary_similarity + keyword_similarity) / 2

            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_cs = cs

        if highest_similarity >= threshold:
            most_similar_pairs.append({"ms_index": ms["index"], "cs_index": most_similar_cs["index"], "similarity": round(
                highest_similarity, 5), "ms_json": ms["json"], "cs_json": most_similar_cs["json"], "ms_content": ms["content"], "cs_content": most_similar_cs["content"]})
        else:
            below_threshold.append(
                {"index": ms["index"], "json": ms["json"], "content": ms["content"]})

    most_similar_pairs.sort(key=lambda x: x["similarity"], reverse=True)
    return most_similar_pairs, below_threshold


ms_summaries = read_json_file("embedding_GPT MS Summary.json")
cs_summaries = read_json_file("embedding_GPT CS Summary.json")
ms_keywords = read_json_file("embedding_GPT MS Keywords.json")
cs_keywords = read_json_file("embedding_GPT CS Keywords.json")

### After testing for best accuracy, found 0.87 to be most accurate as it gives us 3 individual alerts as reward and just 1 loss
similarity_threshold = 0.87

# Find most similar CS alerts for each MS alert
ms_pairs, ms_below_threshold = find_most_similar_pair(
    ms_summaries, cs_summaries, ms_keywords, cs_keywords, similarity_threshold)

# Find most similar MS alerts for each CS alert
cs_pairs, cs_below_threshold = find_most_similar_pair(
    cs_summaries, ms_summaries, cs_keywords, ms_keywords, similarity_threshold)

# Save JSON pairings to Excel
ms_pairs_df = pd.DataFrame(ms_pairs)
cs_pairs_df = pd.DataFrame(cs_pairs)
ms_below_threshold_df = pd.DataFrame(ms_below_threshold)
cs_below_threshold_df = pd.DataFrame(cs_below_threshold)

with pd.ExcelWriter("MS_CS_semantic_pairings_v2.xlsx") as writer:
    ms_pairs_df.to_excel(writer, sheet_name="MS_to_CS_Pairs", index=False)
    cs_pairs_df.to_excel(writer, sheet_name="CS_to_MS_Pairs", index=False)
    ms_below_threshold_df.to_excel(
        writer, sheet_name="MS_Below_Threshold", index=False)
    cs_below_threshold_df.to_excel(
        writer, sheet_name="CS_Below_Threshold", index=False)
