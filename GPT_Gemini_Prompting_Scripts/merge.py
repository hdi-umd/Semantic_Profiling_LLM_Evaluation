import json, os
import  difflib

def cleanup():
    master = "../Output Analysis/final LLM Annotations/mixtral_results.json"

    #load original gt
    original = json.load(open(master, 'r'))
    vis_tasks = json.load(open("./LLM Output/llama3/mixtral_results.json", 'r'))
    
    for item in original:
        if not item: continue
        orig_query = item["query"].lower().replace("  ", " ").replace('"',"'").replace(" ,", ",").replace("' '", "'").replace(" 's", "'s").replace(" -", "-")
        for vis in vis_tasks:
            if not vis: continue
            vis_query = vis["query"].lower().replace("  ", " ").replace('"',"'").replace(" ,", ",").replace("' '", "'").replace(" 's", "'s").replace(" -", "-")
            if difflib.SequenceMatcher(lambda x: x == " ",orig_query.lower(), vis_query.lower()).ratio()>0.9:
                print("updating vis task ", vis["query"])
                # print(f'updating vis task {item["Low-level visualization task"]} to {vis["Low-level visualization task"]}')
                item["Low-level visualization task"] = vis["Low-level visualization task"]
                # print(f'updating vis task classification {item["Low-level visualization task classification"]} to {vis["Low-level visualization task classification"]}')
                item["Low-level visualization task classification"] = vis["Low-level visualization task classification"]
                break
    
    with open(master, "w") as f:
        json.dump(original, f)

if __name__ == "__main__":
    cleanup()