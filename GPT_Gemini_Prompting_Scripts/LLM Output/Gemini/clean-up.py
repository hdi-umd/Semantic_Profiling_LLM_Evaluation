import json, os

def cleanup():
    master = "./gemini_master.json"
    output = []
    queries = set()
    files = [filename for filename in os.listdir("./") if filename.startswith("gemini_results_")]
    for file in files:
        data = json.load(open("./"+file))
        for prompt in data:
            if prompt and prompt['query'] not in queries:
                output.append(prompt)
                queries.add(prompt['query'])
                      
    with open(master, "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    cleanup()