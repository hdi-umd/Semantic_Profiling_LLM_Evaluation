import csv, re, json

def extract_imports(code):
    pattern = r'\b(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import\s+([\w,*]+))\b'
    imports = re.findall(pattern, code)
    import_list = []
    for imp in imports:
        if imp[0]:  # Import statement like: import module
            import_list.append(imp[0])
        else:  # Import statement like: from module import something
            import_list.extend(imp[1].split('.') + imp[2].split(','))
    return import_list

def clean(df, llm):
    imports=set()
    errors=[]
    non_dataframe_res =[]
    matching_df = []
    non_dataframe_pos_match=[]
    blank_transforms=0

    for row in df:
        q = row[f"{llm}_query"]
        llm_output = row[f'{llm}_llm_output']
        gt_output = row[f'{llm}_gt_output']        
               
        imports.update(extract_imports(row[f'{llm}_llm_transform']))
        
        if llm_output=="": 
            blank_transforms+=1
            continue
        if "pandas.core.groupby.generic " in llm_output or llm_output=="Error running code":
            errors.append(llm_output+':-')
            continue
                
        if llm_output.isnumeric():
            non_dataframe_res.append(llm_output)
            continue
        
        if "pandas.core.groupby.generic" in gt_output or gt_output=="Error running code":continue
        if gt_output.isnumeric(): continue

        if "{" not in llm_output :
            non_dataframe_res.append(llm_output)
            if "{" not in llm_output and "{" not in gt_output: #if both llm and gt are not dataframes, then return positive match
                non_dataframe_pos_match.append(llm_output==gt_output)
                continue
            continue
        #attempt to cast json to 
        try:
            llm_out = json.loads(llm_output)
        except json.decoder.JSONDecodeError as e:
            # print(f"error processing {q}: {e}")
            non_dataframe_res.append(llm_output)
            continue

        try:
            gt_out = json.loads(gt_output)
        except Exception as e:
            print(f"error processing gt {q}: {e}")
            # print(gt_output)
            continue
        
        #remove index from both then compare values
        if "index" in llm_out.keys(): del llm_out["index"]
        if "index" in gt_out.keys(): del gt_out["index"]
        matching_df.append(sorted(llm_out.values())==sorted(gt_out.values()))
    
    return{
            "llm": llm,
            # "errors": errors,
            "errors_count": len(errors),
            "imports": imports,
            "imports_count": len(imports),
            "blank_transforms": blank_transforms,
            "non_df_returned_count": len(non_dataframe_res),
            "total_dfs_returned": len(matching_df),
            "matching_df": matching_df.count(True),
            "mismatching_df": matching_df.count(False),
            "non_df_pos_match": non_dataframe_pos_match.count(True)
    }
    

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
        print(len([i for i in data if "pandas.core.groupby.generic" in i["gpt_gt_output"] or  i["gpt_gt_output"] == "Error running code"]))
        out.append(clean(data, key))
    
    headers= out[0].keys()
    filename = f"./results/cleaned_transforms_results.csv"
    with open(filename, 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        csv_writer.writeheader()
        csv_writer.writerows(out)
    