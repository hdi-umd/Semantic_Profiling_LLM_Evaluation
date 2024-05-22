import json

llama = json.load(open("./llama_results.json"))
mixtral = json.load(open("./mixtral_results.json"))
gemini = json.load(open("./gemini_master.json"))
gpt = json.load(open("./gpt4_results.json"))
# def clean(input):
#     output =[]
#     for i in input:
#         i["Mixtral_response"]["query"] = i["key"]
#         output.append(i["Mixtral_response"])

#     return output

def clean(input):
    for i in input:
        # print(i)
        if not i:
            continue
        # if "?" not in i["query"]:
        print(i["query"])
        i["query"]=i["query"].replace(".", "").replace("?", "").replace(" ,", ",").strip()
        print(i["query"])
    return input

with open("./final/llama_results.json", "w") as f:
    json.dump(clean(llama), f)

with open("./final/mixtral_results.json", "w") as f:
    json.dump(clean(mixtral), f)

with open("./final/gpt4_results.json", "w") as f:
    json.dump(clean(gpt), f)

with open("./final/gemini_results.json", "w") as f:
    json.dump(clean(gemini), f)