# Evaluating LLM Semantic Profiling Capabilities
## GPT_Gemini_Prompting_Scripts

Contains the scripts used to send both Batch and Async queries to GPT and Gemini APIs.

## Content
This folder contains the following sub-folders

**batch_input_files:** Contains the output of gpt4-batch-processing.py. All files are formatted according to GPT .jsonl formatting guidelines

**LLM Output:** Contains the LLM responses generated for GPT and Gemini. The llama3 sub-folder within this dir only contains responses for the vis-tasks not the complete annotations.

The folder contains the following files
**prompt.txt:** Text file with complete prompt used to query LLMs

**prompt_vis_task.txt:** Text file containing modified prompt for quering LLMs regarding vis tasks context only. Used for batch processing since OpenAI has limits on how many tokens may be sent in a singl batch

**run_gpt_gemini_queries.py:** Used to send async calls to GPT and Gemini.
**gpt4-batch-processing.py.:** Used to schedule batch processing queries for GPT4.

**query_prep.py:** Used to format nl utterances contained in nl_utterances_corpus.csv for prompting. Output is nl_corpus.json
