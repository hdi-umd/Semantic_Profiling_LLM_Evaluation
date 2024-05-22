"""Used to format the raw nl utterances into a json struct that contains the query and corresponding dataset 
outputfile: nl_corpus.json
"""
import pandas as pd
import json

def format_queries(query_path):
    queries = []
    data = pd.read_csv(query_path)
    #duplicate prompt found that we need to account for What is the relationship between sales and profit for each region?

    datasets = data["dataset"].unique()

    for dataset in datasets:
        if dataset == "GunViolence":
            dd = []
            for dataset in ["data.world_gun_death_in_america.csv", "firearm_deaths_usafacts.csv", "gun-violence-data_01-2013_03-2018.csv"]:
                d = pd.read_csv("../datasets/gun violence datasets/"+dataset.lower())
                dd.append(d.iloc[:10,].to_string())
            prompts = data[data["dataset"]=="GunViolence"].Prompt
            
            for prompt in prompts:
                queries.append({
                    "text": prompt,
                    "dataset": dd
                }) 
            continue
        else:
            dd = pd.read_csv("../datasets/"+str(dataset).lower()+".csv")
            dd = dd.iloc[:10].to_string()
        prompts = data[data["dataset"]== dataset].Prompt
        for prompt in prompts:
            queries.append({
                "text": prompt,
                "dataset": dd
            }) 
    with open("./nl_corpus.json", 'w') as f:
        json.dump(queries, f)

if __name__ == "__main__":
    format_queries("./nl_utterances_corpus.csv")
            
        