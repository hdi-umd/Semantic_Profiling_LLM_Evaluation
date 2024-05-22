
import csv, json

 
def unmatched_ambiguities(csv, llm_json, caller):
    out=[]
    
    data = json.load(open(llm_json))
    # print(len([item for item in data if item["Ambiguity in the query"] !="" and item["Ambiguity resolution"]==""]))
    for item in csv:
        if not item: continue
        if item[f"{caller}_llm match"] !="":
            for prompt in data:
                
                if not prompt: continue
                if item[f'{caller}_query']==prompt['query']:
                    # print(item[f"{caller}_query"], prompt['query'])
                    out.append({
                        'query':prompt["query"],
                        'llm': caller,
                        'llm ambiguity': prompt["Ambiguity in the query"],
                        'llm resolution': prompt["Ambiguity resolution"]
                    })
    return out

def gt_unmatched_ambiguities(csv, caller):
    out=[]
    
    data = json.load(open('./groundtruths.json'))
    # print(len([item for item in data if item["Ambiguity in the query"] !="" and item["Ambiguity resolution"]==""]))
    for item in data:
        if not item: continue
        if item["Ambiguity in the query"] !="":
            for prompt in csv:
                if not prompt: continue
                if  prompt[f'{caller}_gt match']!="" and prompt[f'{caller}_query']==item['query']:
                    # print(item[f"{caller}_query"], prompt['query'])
                    out.append({
                        'query':item["query"],
                        'missed_by': caller,
                        'llm ambiguity': item["Ambiguity in the query"],
                        'llm resolution': item["Ambiguity resolution"]
                    })
    # print(out)
    return out

    
def load_data_file(path):
    data = []
    csv.field_size_limit(100000000)
    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
         
        # Convert each row into a dictionary 
        # and add it to data
        for rows in csvReader:
            data.append(rows)
    # print(data[0])
    return data
if __name__=="__main__":
    files = {
        "gpt":["./results/gpt_ambiguity_results.csv", "../final LLM Annotations/gpt4_results.json"],
        "gemini":["./results/gemini_ambiguity_results.csv","../final LLM Annotations/gemini_results.json"],
        "llama":["./results/llama_ambiguity_results.csv","../final LLM Annotations/llama_results.json"],
        "mixtral": ["./results/mixtral_ambiguity_results.csv","../final LLM Annotations/mixtral_results.json"]
    }
    out=[]
    for key, value in files.items():
        data = load_data_file(value[0])
        # print(len([i for i in data if "pandas.core.groupby.generic" in i["gpt_gt_output"] or  i["gpt_gt_output"] == "Error running code"]))
        out.extend(gt_unmatched_ambiguities(data, key))
        
    
    headers= out[0].keys()
    filename = f"./results/cleaned_ambiguity_results.csv"
    with open(filename, 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        csv_writer.writeheader()
        csv_writer.writerows(out)
    