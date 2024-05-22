import json, csv, difflib

def clean(json_file, csv_file):
    
    for row in csv_file:
        for item in json_file:
            if item and difflib.SequenceMatcher(lambda x: x == " ",item["query"].lower(), row["gpt_query"].lower()).ratio()>0.9:
                if item["Data transformations"] != row["gpt_gt_transform"]: 
                    print(f"change made for {item['query']}")
                    print("old transform: ", item["Data transformations"])
                    item["Data transformations"] = row["gpt_gt_transform"]
                    print("new transform: ", item["Data transformations"],"\n =====================")    

    # Write missing prompts to file.
    print("writing gt to file")
    with open(f"./results/final/updated_groundtruths.json", 'w') as f:
        json.dump(json_file, f)

def load_data_file(path):
    data = []
    csv.field_size_limit(100000000)
    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
         
        # Convert each row into a dictionary 
        # and add it to data
        for rows in csvReader:
            data.append(rows)
    return data
if __name__=="__main__":
    old_data = load_data_file('./old2/gpt_transforms_results.csv')
    gt = json.load(open("./groundtruths.json"))

    clean(gt, old_data)