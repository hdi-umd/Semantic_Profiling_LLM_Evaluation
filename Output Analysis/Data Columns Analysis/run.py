import json, csv, os
from data_transforms import run_single_transform
import  difflib


def analyze_data_columns(llm_codes, gt,q, caller):
    """Here we want to compare the data columns selected by the llms to the datacolumns in gt.
    for each llm, for each query they were provided with how many had 
    1) exact match with gt i.e data column in both gt and llm
    2) negative matches i.e. data colunm in gt but not in llm
    3) missing matches i.e., llm extracted it but not in gt
    4) how many of the inferred data attributes did they positively match?
    input: {"relevant data columns": [str], "Data column classification": [str]}
    """
    # TODO: check inference and keyword match calculations. Should we be comparing the data columns or not?
    #check exact match for datacolumns
    # print(f'{llm_codes["Relevant data columns"]} | {llm_codes["Data column classification"]}')
    # print(f'{gt["Relevant data columns"]} | {gt["Data column classification"]}')
    #handle missing keyword and inference matches

    #get inferred for llm and gt
    llm_inferred = [llm_codes["Relevant data columns"][i].lower().strip() for i in range(len(llm_codes["Data column classification"])) if llm_codes["Data column classification"][i] == "inferred"]
    gt_inferred = [gt["Relevant data columns"][i].lower().strip() for i in range(len(gt["Data column classification"])) if gt["Data column classification"][i] == "inferred"]
    llm_keyword = [llm_codes["Relevant data columns"][i].lower().strip() for i in range(len(llm_codes["Data column classification"])) if llm_codes["Data column classification"][i] == "keyword"]
    gt_keyword = [gt["Relevant data columns"][i].lower().strip() for i in range(len(gt["Data column classification"])) if gt["Data column classification"][i] == "keyword"]
    llm_dv = [llm_codes["Relevant data columns"][i].lower().strip() for i in range(len(llm_codes["Data column classification"])) if llm_codes["Data column classification"][i] == "data value mention"]
    gt_dv = [gt["Relevant data columns"][i].lower().strip() for i in range(len(gt["Data column classification"])) if gt["Data column classification"][i] == "data value mention"]

    return{
    f"{caller}_query":q,
    f"{caller}_positive matches" : [i.strip().lower() for i in llm_codes["Relevant data columns"] if i.strip().lower() in gt["Relevant data columns"]],
    f"{caller}_positive matches count" : len([i.strip().lower() for i in llm_codes["Relevant data columns"] if i.strip().lower() in gt["Relevant data columns"]]),
    f"{caller}_llm only matches": [i.strip().lower() for i in llm_codes["Relevant data columns"] if i.strip().lower() not in gt["Relevant data columns"]],
    f"{caller}_llm only matches count": len([i.strip().lower() for i in llm_codes["Relevant data columns"] if i.strip().lower() not in gt["Relevant data columns"]]),
    f"{caller}_gt only matches": [i for i in gt["Relevant data columns"] if i not in [ j.strip().lower() for j in llm_codes["Relevant data columns"]]],
    f"{caller}_gt only matches count": len([i for i in gt["Relevant data columns"] if i not in [ j.strip().lower() for j in llm_codes["Relevant data columns"]]]),
    f"{caller}_correct column inferences": [i for i in llm_inferred if i in gt_inferred],
    f"{caller}_correct column inferences count": len([i for i in llm_inferred if i in gt_inferred]),
    f"{caller}_incorrect column inferences": [i for i in gt_inferred if i not in llm_inferred],
    f"{caller}_incorrect column inferences count": len([i for i in gt_inferred if i not in llm_inferred]),
    f"{caller}_correct column keyword match": [i for i in llm_keyword if i in gt_keyword],
    f"{caller}_correct column keyword match count": len([i for i in llm_keyword if i in gt_keyword]),
    f"{caller}_incorrect column keyword match": [i for i in gt_keyword if i not in llm_keyword],
    f"{caller}_incorrect column keyword match count": len([i for i in gt_keyword if i not in llm_keyword]),
    f"{caller}_correct data value classifications": [i for i in llm_dv if i not in gt_dv],
    f"{caller}_correct data value classifications count": len([i for i in llm_dv if i not in gt_dv]),
    f"{caller}_incorrect data value classifications": [i for i in gt_dv if i not in llm_dv],
    f"{caller}_incorrect data value classifications count": len([i for i in gt_dv if i not in llm_dv])
    }

def analyze_data_transforms(q,llm_codes, gt, caller):
    """here we want to understand how well the llms perform at correctly identifying the right data transforms.
    for each query, execute the dt presented by gt and llm
    1) how many positive matches between llm and gt tables?
    2) how many differences in llm and gt tables? what and how many columns are different?"""

    dataset = gt["dataset"]
    llm_table = run_single_transform({"query":q,"dataset": dataset, "code": llm_codes["Data transformations"]}, caller=caller)
    gt_table = run_single_transform({"query":q,"dataset": dataset, "code": gt["Data transformations"]})

    return (llm_table == gt_table, llm_table, gt_table) #assuming return from run_single_transform is a dict


def write_to_csv(model, data_context, tranforms):
    headers = data_context.keys()
    filename = f"./results/{model}_data_context_results.csv"
    flag = "a" if os.path.exists(filename) else "w"
    with open(filename, flag) as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        if flag=="w":
            csv_writer.writeheader()
        csv_writer.writerow(data_context)
        f.close()
    
        
    # headers=list({k for d in tranforms for k in d.keys()})
    headers= tranforms.keys()
    filename = f"./results/{model}_transforms_results.csv"
    flag = "a" if os.path.exists(filename) else "w"
    with open(filename, flag) as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        if flag == "w":
            csv_writer.writeheader()
        csv_writer.writerow(tranforms)
        f.close()


def llm_analysis(llm, gt, q, caller):
    # print(llm, gt)
    
    try:
        data_context = analyze_data_columns(
                llm, 
                gt,
                q,
                caller
            )
    except Exception as e:
        print(f"...Error processing data context for {caller} output: {q} \n ...{e}")
        data_context = {
            f"{caller}_query":q,
            f"{caller}_positive matches" : "",
            f"{caller}_positive matches count" : "",
            f"{caller}_llm only matches": "",
            f"{caller}_llm only matches count": "",
            f"{caller}_gt only matches": "",
            f"{caller}_gt only matches count": "",
            f"{caller}_correct column inferences": "",
            f"{caller}_correct column inferences count": "",
            f"{caller}_incorrect column inferences": "",
            f"{caller}_incorrect column inferences count": "",
            f"{caller}_correct column keyword match": "",
            f"{caller}_correct column keyword match count": "",
            f"{caller}_incorrect column keyword match": "",
            f"{caller}_incorrect column keyword match count": "",
            f"{caller}_correct data value classifications": "",
            f"{caller}_correct data value classifications count": "",
            f"{caller}_incorrect data value classifications": "",
            f"{caller}_incorrect data value classifications count": ""
        }

    try:
        dt=analyze_data_transforms(q,
                llm, 
                gt,
                caller
            )
        transforms = {
            f"{caller}_query":q,
            f"{caller}_llm_transform": llm["Data transformations"],
            f"{caller}_gt_transform": gt["Data transformations"],
            f"{caller}_same_data": dt[0],
            f"{caller}_llm_output": dt[1],
            f"{caller}_gt_output":dt[2]
        }
    except Exception as e:
        print(f"...Error processing data transformations for {caller} output: {q} \n ...{e}")
        transforms = {
            f"{caller}_query":q,
            f"{caller}_llm_transform": "",
            f"{caller}_gt_transform": "",
            f"{caller}_same_data": "",
            f"{caller}_llm_output": "",
            f"{caller}_gt_output":""
        }
    return {
        f"{caller}_data_columns": data_context,
        f"{caller}_data_transforms": transforms
    }
    
def run(input_file, caller):
    """run analysis. Final output should be a json """
    
    print(f'starting {caller} analysis......')
    print('loading files......')
    gpt_data = json.load(open(input_file))
    groundtruths = json.load(open("../groundtruths.json"))

    missinggpt=[]
    

    queries = [i["query"] for i in groundtruths]
    x=0

    print("beginning processing of queries")
    for q in queries:
        print(f"processing {x+1} of {len(queries)} queries")
        q = q.lower().replace("  ", " ").replace('"',"'").replace(" ,", ",").replace("' '", "'").replace(" 's", "'s").replace(" -", "-")
        #get all the rows for gt queries
        try:
            # print("loading groundthruths codes for query")
            for item in groundtruths:
                if item and item["query"].lower().replace("  ", " ").replace('"',"'").replace(" ,", ",").replace("' '", "'").replace(" 's", "'s").replace(" -", "-") == q:
                    gt = item
                    # print("gt found", gt)
                    break
            
        except Exception as e:
            print(f"...Encountered an error processing query: '{q}' \n ...{e}")
            x+=1
            continue

        
        try:
            # print("loading gpt codes for query")
            gpt_dt=None
            for i in range(len(gpt_data)):
                item = gpt_data[i]
                if not item: continue
                if item and difflib.SequenceMatcher(lambda x: x == " ",item["query"].lower(), q).ratio()>0.9:
                    gpt_dt = item
                    break
            
            if not gpt_dt: 
                print(f"...query not found in {caller} results")
                missinggpt.append(q)
                file = open(f"./results/{caller}_missing_prompts.txt", "a")
                file.write(f"{str(q)};\n")
                file.close()
            else:
                # print('query found. now analyzing chatgpt4 output')
                
                res = llm_analysis(gpt_dt, gt, q, caller)
                write_to_csv(caller, res[f"{caller}_data_columns"], res[f"{caller}_data_transforms"])
        except Exception as e:
            print(f"...Encountered an error processing query: '{q}' \n ...{e}")
            missinggpt.append(q)
            file = open(f"./results/{caller}_missing_prompts.txt", "a")
            file.write(f"{str(q)};\n")
            file.close()
        x+=1
    
    
    # Write missing prompts to file.
    print("writing missing prompts to file")
    oo = [i for i in groundtruths if i["query"] in missinggpt]
    with open(f"./results/missing{caller}.json", 'w') as f:
        json.dump(oo, f)
    
    print("done!!!")

if __name__=="__main__":
    files={
        "gpt": "../final LLM Annotations/gpt4_results.json",
        "gemini": "../final LLM Annotations/gemini_results.json",
        # "llama": "../final LLM Annotations/llama_results.json",
        # "mixtral": "../final LLM Annotations/mixtral_results.json"
    }
    for key, value in files.items():
        run(value, key)
        