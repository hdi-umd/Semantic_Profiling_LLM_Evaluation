import json, os

def cleanup():
    master = "./mixtral_results.json"
    output = []
    queries = set()
   
    data = json.load(open("./nl_corpus_mistral_final-may.json", 'r')) 
    
    for prompt in data:
        resp = prompt["mistral_response"]
        if resp and not isinstance(resp, str) and "query" in resp.keys():
            if resp["query"] not in queries:
                output.append(resp)
                queries.add(resp["query"])
                 
    with open(master, "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    cleanup()