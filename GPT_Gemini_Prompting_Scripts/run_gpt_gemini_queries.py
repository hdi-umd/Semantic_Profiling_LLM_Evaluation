"""https://towardsdatascience.com/the-proper-way-to-make-calls-to-chatgpt-api-52e635bea8ff"""
import asyncio, aiohttp, time
import json
import yaml, os
import pandas as pd
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

openai_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config['openai']}"
}
gemini_headers = {
    "Content-Type": "application/json"
}

class ProgressLog:
    def __init__(self, total):
        self.total = total
        self.done = 0

    def increment(self):
        self.done = self.done + 1

    def __repr__(self):
        return f"Done runs {self.done}/{self.total}."
    
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(2), before_sleep=print, retry_error_callback=lambda _: None)
async def openai_get_completion(content, session, semaphore, progress_log):
    async with semaphore:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=openai_headers, json={
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_object"},
            "top_p": 0.1
        }) as resp:

            response_json = await resp.json()

            progress_log.increment()
            print(progress_log)
        
            return json.loads(response_json["choices"][0]['message']["content"])

# google_api = config["google_h"]
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5), before_sleep=print, retry_error_callback=lambda _: None)
async def gemini_get_completion(content, session, semaphore, progress_log, google_api):
    async with semaphore:
        async with session.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={google_api}", headers=gemini_headers, json={
            "contents": [{
                "parts":[{
                    "text": content
                }]
            }],
            "generationConfig": {
                "topP": 0.8,
            }
        }) as resp:

            response_json = await resp.json()

            progress_log.increment()
            print(progress_log)
            with open("../LLM Output/gemini_query_tracker.txt", "a") as f:
                f.write("index:{}, {}\n".format(progress_log.done-1, content.split("\n")[-1],))

            return json.loads(response_json["candidates"][0]["content"]['parts'][0]["text"])

async def get_completion_list(content_list, max_parallel_calls, timeout, api="openai", apikey=""):
    semaphore = asyncio.Semaphore(value=max_parallel_calls)
    progress_log = ProgressLog(len(content_list))
    if api=="gemini":
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
            return await asyncio.gather(*[gemini_get_completion(content, session, semaphore, progress_log, apikey) for content in content_list])
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
        return await asyncio.gather(*[openai_get_completion(content, session, semaphore, progress_log) for content in content_list])


async def query(queries):
    # input should be a list of dicts with {dataset:"", text:""}
    messages = []
    with open("./prompt.txt", "r") as f:
        prompt = f.read()
   
    for q in queries:
        # if q["text"].replace(".", "").replace("?", "").replace(" ,", ",").strip() not in missing:  # TODO: comment if this is first run for LLM.
        messages.append( f'{prompt} \n dataset:{q["dataset"]} \n query:{ q["text"]}')
    
    print("Starting queries to Openai API")
    start_time = time.perf_counter()
    res = await get_completion_list(content_list=messages, max_parallel_calls=50, timeout=150)
    print("Time elapsed: ", time.perf_counter() - start_time, "seconds.")
    with open("./LLM Output/gpt4_results.json", 'w') as f:
        json.dump(res, f)

   
    print("Starting queries to gemini API")
    start_time = time.perf_counter()
    res = await get_completion_list(content_list=messages, max_parallel_calls=50, timeout=150, api="gemini", apikey=config["google_h"])
    print("Time elapsed: ", time.perf_counter() - start_time, "seconds.")
    with open("./LLM Output/Gemini/gemini_results.json", 'w') as f:
        json.dump(res, f)
    
def gemini_cleanup():
    master = "./LLM Output/gemini_master.json"
    output = []
    queries = set()
    files = [filename for filename in os.listdir("../LLM Output/gemini/") if filename.startswith("gemini_results_")]
    for file in files:
        data = json.load(open("../LLM Output/gemini/"+file))
        for prompt in data:
            if prompt and prompt['query'] not in queries:
                output.append(prompt)
                queries.add(prompt['query'])
                
    #sanity check. Make sure no queries from ground truths are missing
    gt = json.load(open("../groundtruths.json"))
    missing =[]
    for i in gt:
        l = 0
        for q in output:
            if i["query"] == q["query"]:
                l+=1
                if l>1:
                    print("found duplicate", i["query"], f"count {l}")
        if l==0:
            missing.append({
                "query": i["query"],
                "dataset": i["dataset"]
            })
    print(f"total missing: {len(missing)}")       
    with open(master, "w") as f:
        json.dump(output, f)

    with open("gemini_mising_queries.json", "w") as f:
        json.dump(missing, f)
    
    
def run():
    print("starting....")
    queries = json.load(open("../nl_corpus.json"))
    asyncio.run(query(queries=queries))

if __name__ == "__main__":
    run()