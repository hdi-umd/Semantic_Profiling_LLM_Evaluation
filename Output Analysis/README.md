# Evaluating LLM Semantic Profiling Capabilities
## Output Analysis

Contains the scripts used to evaluate the responses generated by the LLMs evaluated in this study. 


## Instructions
Each sub-folder contains scripts to execute the three analyses performed in the study. Each analyses can be executed using by performing the following actions:
- Navigate into the corresponding sub folder for the analyses you want to perform
- Execute the run.py file by running the following code in the terminal `python run.py`
- Once the script is done running, the output files can be found in the results folder.
- To view the charts and statistical analyses on the output files, you can open and execute the R scripts in R-studio or using your prefered tool.

## Content
This project contains the following sub-folders

**Ambiguity Analysis:** Contains all the files needed to perform the analyses on uncertainties identified in utterances

**Data Columns Analysis:** Contains the files needed to perform the analyses on data column identification and data tranforms code generation and evaluation. 

**Vis Tasks Analysis:** Contains the files needed to perform the analyses on Vis task and vis goal identification. 

## Handling Errors in Data Transformation Code
While evaluating the data transformations, we found that even though we instructed the LLMs not to return code that creates visualizations or perform complex analysis we found 31 instances where the LLMs violated these instructions (gpt:1, gemini:0, llama:15, mixtral:15). We found imports for matplotlib (among other libraries) and corresponding calls to `.plot()' in the code. We also found instances where there were codes that tried to run k-means clustering. We excluded such code from our analysis. Furthermore, while executing the data transformations, we found that 385 of the transformations raised errors of various kinds (gpt:59, gemini:96, llama:119, mixtral:111). We also found that some of the data transformation code returned raw values and not data tables (gpt:66, gemini:90, llama:57, mixtral:52). For our human annotation, we prioritized having data tables (multiple or single columns) as the output of our analysis. As such, we cannot evaluate these responses and decided to remove them from our analysis.