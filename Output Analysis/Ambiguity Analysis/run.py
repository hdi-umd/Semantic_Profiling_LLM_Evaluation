import json, csv, os
from sentence_transformers import SentenceTransformer, util
import  difflib
    
def analyze_ambiguities(llm_codes, gt,q, caller):
    """Here the goal is understanding how well the llms perform at detecting ambiguity. 
    for each llm find out 
    1) how many queries did it positively detect ambiguities in? i.e. ambiguity in gt
    2) how many queries did it detect ambiguity missed by humans? i.e. ambiguity not in gt
    3) how many queries did it miss ambiguities? i.e. ambiguity in gt but not found by llm
    4) for positve matches what is the cosine sim of ambiguities?"""
    return{
        f"{caller}_query":q,
        f"{caller}_positive match": "Ambiguity found by both llm and gt" if len(llm_codes["Ambiguity in the query"]) > 0 and len(gt["Ambiguity in the query"])>0 else "",
        f"{caller}_llm match": "Ambiguity found by llm only" if len(llm_codes["Ambiguity in the query"])>0 and len(gt["Ambiguity in the query"])==0 else "",
        f"{caller}_gt match": "Ambiguity found by gt only" if len(llm_codes["Ambiguity in the query"])==0 and len(gt["Ambiguity in the query"])>0 else "",
        f"{caller}_resolution positive match": "Resolution found by both llm and gt" if len(llm_codes["Ambiguity resolution"]) > 0 and len(gt["Ambiguity resolution"])>0 else "",
        f"{caller}_resolution llm match": "Resolution found by llm only" if len(llm_codes["Ambiguity resolution"])>0 and len(gt["Ambiguity resolution"])==0 else "",
        f"{caller}_resolution gt match": "Resolution found by gt only" if len(llm_codes["Ambiguity resolution"])==0 and len(gt["Ambiguity resolution"])>0 else "",
        f"{caller}_ambiguity similarity match": calculate_topic_similarity(llm_codes["Ambiguity in the query"], gt["Ambiguity in the query"]) if len(llm_codes["Ambiguity in the query"])>0 and len(gt["Ambiguity in the query"])>0 else "",
        f"{caller}_resolution similarity match": calculate_topic_similarity(llm_codes["Ambiguity resolution"], gt["Ambiguity resolution"]) if len(llm_codes["Ambiguity resolution"])>0 and len(gt["Ambiguity resolution"])>0 else ""
    }

def calculate_topic_similarity(llm_text, gt_text):
     # #initialize model
    model = SentenceTransformer('stsb-roberta-large')

    # # encode list of sentences to get their embeddings
    embedding1 = model.encode(llm_text, convert_to_tensor=True)
    embedding2 = model.encode(gt_text, convert_to_tensor=True)

    # #compute similarity scores of the two embeddings
    cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)
    cosine_scores = cosine_scores.numpy().transpose()
    
    
    return cosine_scores[0][0]


def write_to_csv(model, ambiguity_context):
    # headers=list({k for d in ambiguity_context for k in d.keys()})
    headers = ambiguity_context.keys()
    filename = f"./results/{model}_ambiguity_results.csv"
    flag = "a" if os.path.exists(filename) else "w"
    with open(filename, flag) as f:
        csv_writer = csv.DictWriter(f, fieldnames=headers)
        if flag=="w":
            csv_writer.writeheader()
        csv_writer.writerow(ambiguity_context)
        f.close()

def llm_analysis(llm, gt, q, caller):
    try: 
        ambiguity_context = analyze_ambiguities(
                llm, 
                gt,
                q,
                caller
        )
    except Exception as e:
        print(f"...Error processing ambiguities for {caller} output: {q} \n ...{e}")
        ambiguity_context = {
            f"{caller}_query":q,
            f"{caller}_positive match": "",
            f"{caller}_llm match": "",
            f"{caller}_gt match": "",
            f"{caller}_resolution positive match": "",
            f"{caller}_resolution llm match": "",
            f"{caller}_resolution gt match": "",
            f"{caller}_ambiguity similarity match": "",
            f"{caller}_resolution similarity match": ""
        }
    return {
        f"{caller}_ambiguity": ambiguity_context
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
                write_to_csv(caller, res[f"{caller}_ambiguity"])
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
<<<<<<< HEAD
<<<<<<< HEAD
        "llama": "../final LLM Annotations/llama_results.json",
        "mixtral": "../final LLM Annotations/mixtral_results.json"
=======
        # "llama": "../final LLM Annotations/llama_results.json",
        # "mixtral": "../final LLM Annotations/mixtral_results.json"
>>>>>>> 39fba0656289cbc7f54bd0386e7de2762b6e44cb
=======
        # "llama": "../final LLM Annotations/llama_results.json",
        # "mixtral": "../final LLM Annotations/mixtral_results.json"
>>>>>>> 39fba0656289cbc7f54bd0386e7de2762b6e44cb
    }
    for key, value in files.items():
        run(value, key)
        