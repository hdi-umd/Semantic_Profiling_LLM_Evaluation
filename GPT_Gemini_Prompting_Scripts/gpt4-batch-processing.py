import json
from openai import OpenAI
import yaml, os


with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

client = OpenAI(api_key=config["openai"])

def format_queries_jsonl(queries):
    messages = []
    with open("./prompt_vis_task.txt", "r") as f:
        prompt = f.read()

    print("formatting queries")
    
    for i in range(len(queries)):
        q=queries[i]
        # messages.append( 
        #     f'{prompt} \n dataset:{q["dataset"]} \n query:{ q["text"]}')
        messages.append(
            {
            "custom_id": f'request-{i}', 
            "method": "POST", "url": "/v1/chat/completions", 
            "body": {
                "model": "gpt-4-turbo", 
                "messages": [
                    {"role": "system", "content": f'{prompt}'},
                    {"role": "user", "content": f'query:{ q["text"]}'}
                ],
                "response_format": {"type": "json_object"},
                "top_p": 0.1
                }
            }
        )
    with open("./batch_input_files/batch_1.jsonl", "w") as f:
        for item in messages[:44]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_2.jsonl", "w") as f:
        for item in messages[44:88]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_3.jsonl", "w") as f:
        for item in messages[88:132]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_4.jsonl", "w") as f:
        for item in messages[132:176]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_5.jsonl", "w") as f:
        for item in messages[176:220]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_6.jsonl", "w") as f:
        for item in messages[220:264]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_7.jsonl", "w") as f:
        for item in messages[264:308]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_8.jsonl", "w") as f:
        for item in messages[308:352]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_9.jsonl", "w") as f:
        for item in messages[352:396]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_10.jsonl", "w") as f:
        for item in messages[396:440]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_11.jsonl", "w") as f:
        for item in messages[440:484]:
            f.write(json.dumps(item)+ "\n")
    with open("./batch_input_files/batch_12.jsonl", "w") as f:
        for item in messages[484:500]:
            f.write(json.dumps(item)+ "\n")
def schedule_batch():
    
    #load file names
    with open("./batch_input_files/file_ids.txt", "r") as f:
        files=f.read().rstrip()
    i=0
    batch_input_file_id = files[i]
    batchdata = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
        "description": "LLM Eval VIS"
        }
    )
    print(batchdata)
    with open("./gpt_batch_data.json", 'w') as f:
        obj = json.dumps(batchdata.__dict__)
        json.dump(obj, f)

def upload_files():
    file_ids=[]
    for i in range(12):
        batch_input_file = client.files.create(
        file=open(f'./batch_input_files/batch_{i+1}.jsonl', "rb"),
            purpose="batch"
        )
        print("file created: ", batch_input_file.id)
        file_ids.append(batch_input_file.id)
    with open("./batch_input_files/file_ids.txt", "w") as f:
        for item in file_ids:
            f.write(item+ "\n")
        
if __name__ == "__main__":
    print("starting....")
    # queries = json.load(open("./nl_corpus.json"))
    # format_queries_jsonl(queries=queries)
    # schedule_batch()
