# SSME---Semantic_Search_Pairing_Method
NuHarbor Security, Almanna Cyber, The Cybersecurity Polyglot Project

# Idea Title: Semantic Search Pairing Method (SSPM)

Approach: Use a combination of natural language processing (NLP) techniques, such as GPT-3.5-turbo, recursive search, and semantic search, to create a common ontology for security events across multiple providers. By defining the training method for the model on the cybersecurity events from Microsoft and CrowdStrike, I aim to make the semantic search pairing method extensible to new providers and adaptable to the changing security landscape.

Architecture: The architecture of my solution includes the following components:

1. Preprocessing Module: Standardizes and cleans the input data for further processing.
2. Summary & Keywords Generation: Defines the characteristics and contextual meaning of the alert identity.
3. Semantic Search & Pairing Module: Performs semantic search on a vector database to find the most similar summary, ensuring accurate pairings.
4. NLP Model: Processes the preprocessed data using GPT 3.5 Turbo with highly specific prompt engineering to map events to the common ontology.

```python
prompt = f"Perform Abstractive Text Summarization to state the cybersecurity alert name and Quote relevant key characteristics of the alert content, then generate a description of the following cybersecurity alert content:\n{content}\n Summarization should be a concise definition of the alert that can be applicable to any cybersecurity vendors; do not include user name, IP addresses, ID, non-alert information, specific account information, or file path information. The format should be as follows:\n\nAlert Name: <Name> . - \nKey Characteristics: <Keywords> . - \nCybersecurity Alert Description: <Description> \n<<END>>"
```

1. Output Module: Presents the translated events in the unified format for security analysts. Results are appended at the end of the JSON dictionaries.
2. Monitoring & Updating Module: Monitors the model's performance and updates/retrains as needed.

Future: 

- Cross validate between MS_to_CS_Pairs and CS_to_MS_Pairs may give more matches and more accurately represent the standalone alerts that does not have a high similarity threshold.

Strengths:

- Unified event representation across multiple providers.
- Extensibility to incorporate new providers with minimal effort, small vector database to maintain.
- Adaptable to the evolving security landscape by updating/retraining the model.
- Fast (~1s per alerts) and accurate semantic search and pairing (85.71% accuracy).

Weaknesses:

- High dependency on the quality and diversity of training data.
- Possibility of false common ontology appended with JSON that are not yet recognized by the model, perhaps due to different semantic contextual structures or confusing (to the machine) wording.
- Time-consuming iteration process for prompt-engineering and semantic search pairing (Data management and organization and pairing).

Maintenance & Extension:

- Periodic retraining of the model to adapt to the changing security landscape.
- Updating the preprocessing module to handle new data formats as more providers are added.
- Adding new endpoint security providers by including their events in the training data and retraining the model.
- Refining semantic search pairing and database organization/extraction methods as needed.

Project overview and reflection:
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
