# SSPM---Semantic_Search_Pairing_Method
NuHarbor Security, Almanna Cyber, The Cybersecurity Polyglot Project


## Developer and coding-agent handoff (source review: 2026-10-15)

A developer exploring this repository is reviewing a cybersecurity research prototype that pairs Microsoft and CrowdStrike security-event examples and attaches a shared description (a common ontology). The repository preserves numbered experiments, intermediate spreadsheets and generated embeddings. It does not yet document a reproducible current environment or a complete automatic pipeline.

**Accuracy provenance:** the historical **85.71%** figure is a manually assisted result. [Step 3](step3_accuracy_test_85.71%25.py) compares the `MS_to_CS_Pairs` worksheet with `Manual_Updated_Key_v1.xlsx`, then unconditionally adds three matches documented as manual inspection before printing the percentage. Its saved output comment reports **84 matches / 98 key rows**, including that adjustment. This is historical evidence, not a current automatic accuracy benchmark. Current reproducible accuracy has not been established.

**Start by inspecting, not running the scripts.** From the repository root, `git status --short` shows local changes and `git ls-tree --name-only HEAD` lists committed files without executing the pipeline. Preserve the spreadsheets and generated artifacts before experiments, and work in a disposable copy. Several scripts execute at top level when run or imported; their output paths are relative to the working directory. Step 0 rewrites its input JSON, most later stages overwrite outputs, and step 7 appends to an output file.

### Inputs, manual stages and outputs

The order below follows the existing source; it is an orientation map, not a verified run recipe.

| Stage | Required inputs | What the existing script does |
| --- | --- | --- |
| [0: clean event JSON](step0_clear_JSON_id_timestamp.py) | `All/*.json` | Removes selected timestamp/ID fields recursively and **rewrites the matched input files in place**. |
| [1: populate the pairing key](step1_updated_key.py) | `Key.xlsx`, `All/*.json` | Writes `Updated_Key_v1.xlsx`. The final source comments require **manually correcting 30 cells** and saving `Manual_Updated_Key_v1.xlsx` before step 3. |
| [2.0: generate summaries and keywords](step2.0_generate_completions.py) | `All/*.json`, provider credentials | Makes model calls and writes `summary_database_vf.xlsx`. |
| [2.1: generate embeddings](step2.1_kw_summary_embeddings.py) | `summary_database_vf.xlsx`, provider credentials | Makes embedding calls and writes four `embedding_GPT ... Summary/Keywords.json` files, separated by provider. |
| [2.2: pair embeddings](step2.2_semantic_similarity.py) | Those four embedding files | Compares summary/keyword vectors and writes `MS_CS_semantic_pairings_v2.xlsx` with directional pair and below-threshold worksheets. |
| [3: inspect historical pair matching](step3_accuracy_test_85.71%25.py) | `MS_CS_semantic_pairings_v2.xlsx`, `Manual_Updated_Key_v1.xlsx` | Prints an exact-pair match count **plus the fixed three-match manual adjustment**. Running this script is not an unadjusted accuracy evaluation. |
| [4: generate the common descriptions](step4_generate_common_ontology.py) | Pairing workbook, manually corrected key, provider credentials | Generates descriptions for matched rows and writes `Manual_Updated_Key_v1_with_ontology.xlsx`. |
| [5: build the reference dataset](step5_training_v1.py) | Ontology workbook, provider credentials | Embeds paired examples and writes `training_dataset_v1.json`. Despite the filename's “training” label, this script builds reference entries and vectors; it does not call a model fine-tuning API. |
| [6: apply the reference dataset](step6_testing.py) | `training_dataset_v1.json`, provider summary embeddings, `CS-MS-Test-Data.json`, provider credentials | The active enrichment loop handles at most the first ten loaded rows (lines 123–131); the output loop then writes **all loaded rows** to `CS-MS-Test-Data_with_output.json` (lines 134–136). The `All-CS` / `All-MS` demonstrations are inactive text inside a triple-quoted string (lines 141–216), not active input requirements. This is not a general benchmark runner. |
| [7: explore Sysmon examples](step7_sysmon.py) | `Archive/sysmon_all.json`, reference dataset, summary embeddings, provider credentials | Uses embeddings and a generated-description fallback; **appends** to `Archive/sysmon_with_output.json`. Its printed ratio uses a fixed denominator of 28. |

### Setup boundaries before attempting regeneration

- The inspected commit contains generated spreadsheets, event JSON and embeddings, but no `All/` directory for stages 0, 1 and 2.0. Those raw inputs and the manual spreadsheet decisions must be supplied and checked separately. `All-CS/` and `All-MS/` appear only in inactive step 6 demonstration text and are not active step 6 requirements. Shipped artifacts do not establish that regeneration succeeds.
- Imports identify `pandas`, `numpy`, `openai`, `tenacity` and `xlsxwriter`. No dependency manifest, supported Python version, package pins or XLSX reader-engine contract is present. An installation command is intentionally not claimed to work.
- Provider stages read a local `openaiapikey.txt` file and use the legacy `openai.ChatCompletion.create` / `openai.Embedding.create` interfaces. Confirm SDK/model compatibility and input-data approval before making external calls; keep credentials outside version control. This handoff has not tested provider access or current compatibility.
- No install, script import/run, provider call or benchmark was performed for this source review. The original timing observations below are historical and have not been reproduced.

The review above describes source at commit [94468b8](https://github.com/HomenShum/SSPM---Semantic_Search_Pairing_Method/tree/94468b8f70058e5d8b8c017da15749663bc73114). The linked scripts are the execution contract to inspect before changing the algorithm or claiming a new result.

Documentation updates: [README history](CHANGELOG/docs/readme.md).

## Original project notes (historical)

These notes preserve the original research design and reflections. Some described capabilities are goals or experiments; use the source map above to identify the implemented steps.

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
- Historical observations: about 1s per alert and 85.71% manually assisted pair matching; see the provenance and limitations above. Neither is a current reproduced benchmark.

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

Historical result and rationale:
The recorded pair-matching result was 85.71%, including the three manually inspected matches added by step 3.
This result motivated the next experiment; it does not establish current automatic matching accuracy or downstream performance.
    The alert's json data structure differ in IP, ID, and timestamp related information
    The semantic structure and contextual meaning that identifies each alert does not change.  
    Therefore, Semantic search became very handy: it allows small training dataset, and with the right structuring, we can perform semantic search to very quickly determine the common ontology. 

Next experiment: build the semantic-search reference dataset:
    The corresponding JSON pairs is concatenated and written into training_dataset_v1.json
    The embeddings are then generated for the training_dataset_v1.json
    The corresponding common ontology output is also written into th training_dataset_v1.json
With this vector database, we can now perform semantic search pairing method to quickly determine the common ontology of the alert.

Historical timing note: 83.82 seconds was reported for 100 alerts from CS-MS-Test-Data. The environment and procedure are not bound here, and this timing has not been reproduced.

Post-hackathon reflections:
This entire trial run result demonstrates the power of NLP tool when combined with an optimized vector database management system. 
The small reference dataset and the historical matching/timing observations motivated further exploration; they do not establish current accuracy or throughput.
It just takes a long time to iterate the prompt and the semantic search pairing method and database organization/extraction method for it to work correctly.
The semantic search pairing method is very powerful and can be used for many different applications.
