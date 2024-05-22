import json, csv, os
import  difflib


def analyze_visual_task_and_goals(llm_codes, gt,q, caller):
    """Here we want to compare the data columns selected by the llms to the datacolumns in gt.
    for each llm, for each query they were provided with how many had 
    1) exact match with gt i.e data column in both gt and llm
    2) negative matches i.e. data colunm in gt but not in llm
    3) missing matches i.e., llm extracted it but not in gt
    4) how many of the inferred data attributes did they positively match?"""

    llm_task_inferences = [llm_codes["Low-level visualization task"][i].strip().lower() for i in range(len(llm_codes["Low-level visualization task classification"])) if llm_codes["Low-level visualization task classification"][i] == "inferred" ]
    gt_task_inferences = [gt["Low-level visualization task"][i].strip().lower() for i in range(len(gt["Low-level visualization task classification"])) if gt["Low-level visualization task classification"][i] == "inferred" ]
    return{
    f"{caller}_query":q,
    f"{caller}_positive matches" : [i.strip().lower() for i in llm_codes["Low-level visualization task"] if i.strip().lower() in gt["Low-level visualization task"]],
    f"{caller}_llm only matches": [i.strip().lower() for i in llm_codes["Low-level visualization task"] if i.strip().lower() not in gt["Low-level visualization task"]],
    f"{caller}_gt only matches": [i.strip().lower() for i in gt["Low-level visualization task"] if i.strip().lower() not in llm_codes["Low-level visualization task"]],
    f"{caller}_correct task inferences": [i for i in llm_task_inferences if i in gt_task_inferences],
    f"{caller}_missed task inferences": [i for i in gt_task_inferences if i in llm_task_inferences],
    f"{caller}_correct goal classifications": llm_codes["Visualization goal"][0] == gt["Visualization goal"][0],
    f"{caller}_missing goal classifications": len(llm_codes["Visualization goal"])==0 and len(gt["Visualization goal"])>0,
    f"{caller}_positive matches count" : len([i.strip().lower() for i in llm_codes["Low-level visualization task"] if i.strip().lower() in gt["Low-level visualization task"]]),
    f"{caller}_llm only matches count": len([i.strip().lower() for i in llm_codes["Low-level visualization task"] if i.strip().lower() not in gt["Low-level visualization task"]]),
    f"{caller}_gt only matches count": len([i.strip().lower() for i in gt["Low-level visualization task"] if i.strip().lower() not in llm_codes["Low-level visualization task"]]),
    f"{caller}_correct task inferences count": len([i for i in llm_task_inferences if i in gt_task_inferences]),
    f"{caller}_missed task inferences count": len([i for i in gt_task_inferences if i in llm_task_inferences])
    }

def analyze_visual_task_and_goals_similarity(llm_codes, gt,q, caller):
    """Here we want to compare the data columns selected by the llms to the datacolumns in gt.
    for each llm, for each query they were provided with how many had 
    1) exact match with gt i.e data column in both gt and llm
    2) negative matches i.e. data colunm in gt but not in llm
    3) missing matches i.e., llm extracted it but not in gt
    4) how many of the inferred data attributes did they positively match?"""


    llm_task_inferences = [llm_codes["Low-level visualization task"][i].strip().lower() for i in range(len(llm_codes["Low-level visualization task classification"])) if llm_codes["Low-level visualization task classification"][i] == "inferred" ]
    gt_task_inferences = [gt["Low-level visualization task"][i].strip().lower() for i in range(len(gt["Low-level visualization task classification"])) if gt["Low-level visualization task classification"][i] == "inferred" ]
    
    pos_matches = []
    gt_only = []
    for code in llm_codes["Low-level visualization task"]:
        if code.lower().strip() in gt["Low-level visualization task"]:
            pos_matches.append(code)
            continue
        else:
            #check if it is synonym
            for gt_code in gt["Low-level visualization task"]: #should handle casses such as 'distribution' instead of 'characterize distribution'
                if code.lower().strip() in gt_code: 
                    pos_matches.append(code)
                    break
                else: #not found by llm
                    gt_only.append(gt_code)
    
    llm_only = set(llm_codes["Low-level visualization task"]) - set(pos_matches)        #found by llm alone  
            
    return{
    f"{caller}_query":q,
    f"{caller}_positive matches" : pos_matches,
    f"{caller}_llm only matches": llm_only,
    f"{caller}_gt only matches": gt_only,
    f"{caller}_correct task inferences": [i for i in llm_task_inferences if i in gt_task_inferences],
    f"{caller}_missed task inferences": [i for i in gt_task_inferences if i in llm_task_inferences],
    # f"{caller}_correct goal classifications": llm_codes["Visualization goal"][0] == gt["Visualization goal"][0],
    # f"{caller}_missing goal classifications": len(llm_codes["Visualization goal"])==0 and len(gt["Visualization goal"])>0,
    f"{caller}_positive matches count" : len(pos_matches),
    f"{caller}_llm only matches count": len(gt_only),
    f"{caller}_gt only matches count": len(gt_only),
    f"{caller}_correct task inferences count": len([i for i in llm_task_inferences if i in gt_task_inferences]),
    f"{caller}_missed task inferences count": len([i for i in gt_task_inferences if i in llm_task_inferences])
    }



def write_to_csv(model, vis_context):
    
    # headers=list({k for d in vis_context for k in d.keys()})
    headers = vis_context.keys()
    filename = f"./results/{model}_vis_context_results.csv"
    flag = "a" if os.path.exists(filename) else "w"
    with open(filename, flag) as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        if flag=="w":
            csv_writer.writeheader()
        csv_writer.writerow(vis_context)
        f.close()


def llm_analysis(llm, gt, q, caller):
    try: 
        vis_context = analyze_visual_task_and_goals_similarity(
                    llm, 
                    gt,
                    q,
                    caller
            )
    except Exception as e:
        print(f"...Error processing vis context for {caller} output: {q} \n ...{e}")
        vis_context = {
            f"{caller}_query":q,
            f"{caller}_positive matches" : "",
            f"{caller}_llm only matches": "",
            f"{caller}_gt only matches": "",
            f"{caller}_correct task inferences": "",
            f"{caller}_missed task inferences": "",
            f"{caller}_correct goal classifications": "",
            f"{caller}_missing goal classifications": "",
            f"{caller}_positive matches count" : "",
            f"{caller}_llm only matches count": "",
            f"{caller}_gt only matches count": "",
            f"{caller}_correct task inferences count": "",
            f"{caller}_missed task inferences count": ""
        }

   
    return {
        f"{caller}_vis_context": vis_context,
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
                item["query"] = item["query"].lower().replace("  ", " ").replace('"',"'").replace(" ,", ",").replace("' '", "'").replace(" 's", "'s").replace(" -", "-")
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
                write_to_csv(caller, res[f"{caller}_vis_context"])
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
<<<<<<< HEAD
<<<<<<< HEAD
        "gpt": "../final LLM Annotations/gpt4_results.json",
        "gemini": "../final LLM Annotations/gemini_results.json",
=======
        # "gpt": "../final LLM Annotations/gpt4_results.json",
        # "gemini": "../final LLM Annotations/gemini_results.json",
>>>>>>> 39fba0656289cbc7f54bd0386e7de2762b6e44cb
=======
        # "gpt": "../final LLM Annotations/gpt4_results.json",
        # "gemini": "../final LLM Annotations/gemini_results.json",
>>>>>>> 39fba0656289cbc7f54bd0386e7de2762b6e44cb
        "llama": "../final LLM Annotations/llama_results.json",
        "mixtral": "../final LLM Annotations/mixtral_results.json"
    }
    for key, value in files.items():
        run(value, key)
        