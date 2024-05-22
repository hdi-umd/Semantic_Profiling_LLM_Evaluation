import json, os

def cleanup():
    master = "./gpt_results.json"
    output = []
    queries = set()
    files = [filename for filename in os.listdir("./") if filename.startswith("batch_")]
    for file in files:
        with open("./"+file, 'r') as f:
            data = [json.loads(i) for i in f]
        
        for prompt in data:
            resp = json.loads(prompt["response"]["body"]["choices"][0]['message']["content"])
            if resp["query"] not in queries:
                output.append(resp)
                queries.add(resp["query"])
                 
    with open(master, "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    cleanup()