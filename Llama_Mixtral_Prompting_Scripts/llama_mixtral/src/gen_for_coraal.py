import json
from llmtuner import ChatModel
from llmtuner.extras.misc import torch_gc
from tqdm import tqdm

def load_chat(chat_path):
    with open(chat_path, 'r') as file:
        data = json.load(file)
    return data

def save_chat(chats, chat_path):
    with open(chat_path, 'w') as file:
        json.dump(chats, file, indent=4)

def main():
    chat_model = ChatModel()
    messages = []
    print("Welcome to the CLI application, use `clear` to remove the history, use `exit` to exit the application.")

    file_path = 'data/nl_corpus.json'
    chats = load_chat(file_path)
    responses = []
    i = 0
    system_instruction = """
        You are a visualization design expert trying to resolve ambiguity in user queries on a dataset. You have been provided with a dataset and a query, and asked to identify the following content in the query:
        1. Relevant data columns: Data columns that may have been mentioned in the query
        2. Data column classification: Specify how each column was identified. Was it a keyword mentioned, a synonym, a data value, or inferred based on the context
        3. Low-level visualization task: Which visualization task can be identified in the query? For instance, correlation, find extremum, relationship, comparison, etc
        4. Low-level visualization task classification: is it a keyword, synonym, or inferred based on context
        5. Visualization goal: Is this targeted (i.e., a specific visualization goal in mind) or exploratory (I.e., no specific goal in mind)
        6. Ambiguity in the query. Do not include anything related to plotting the data. return empty string if no ambiguity
        7. Ambiguity resolution which should be focused on the necessary data transformations. return empty string if no ambiguity resolution
        8. Data transformations: what data transformations can be used to generate a data table that answers the query. Result should be a pandas expression. Do not include plots
        9. Data transformation operation: what are the main operations performed in the data transformation? E.g., groupby, min, filter, select
        10. New column name: a new calculated column referenced in the query. return empty string if no new column name
        11. New column derivation: an explicit derivation formulae for a new column in query. return empty string if no new column name
        12. Missing column: a column name referenced in the query that is neither a synonym of an existing column nor include a derivation. return empty string if no new column name

        Your output should be formatted as a JSON.

        For example 

        dataset: Entity	Code	Year	AFF value added (% of GDP)	GDP per capita	Population	Continent
        Abkhazia	OWID_ABK	2015				Asia
        Afghanistan	AFG	2002	38.62789	1280.4631	21000258	Asia
        Afghanistan	AFG	2003	37.418854	1292.3335	22645136	Asia
        Algeria	DZA	1999	11.10698	8584.071	30346086	Africa
        Algeria	DZA	2000	8.395048	8786.19	30774624	Africa

        query: What is the trend of GDP of  some country, e.g. Albania?
        { "query": "What is the trend of GDP of  some country, e.g. Albania",
        "Relevant data columns": ["GDP per capita", "Year", "Entity"],
        "Data column classification": ["synonym", "inferred", "data value mention"],
        "Low-level visualization task": ["trend"],
        "Low-level visualization task classification": ["keyword",],
        "Visualization goal": ["targeted"],
        "Ambiguity in the query": "",
        "Ambiguity resolution": "",
        "Data transformations": "df = df[df["Entity"]=="Albania"]; df[["Entity", "Year", "GDP per capita"]]",
        "Data transformation operation": ["filter", "select"],
        "New Column Name": "",
        "Derivation Specification": "",
        "Missing Data Column":""
        }

        query: Which countries have the highest and lowest GDPs?
        {"query":"Which countries have the highest and lowest GDPs?",
        "Relevant data columns": ["Entity","GDP per capita"],
        "Data column classification": ["inferred","keyword", "keyword", "inferred", "inferred"],
        "Low-level visualization task": ["retrieve value", "find extreme"],
        "Low-level visualization task classification": ["inferred", "inferred"],
        "Visualization goal": ["targeted"],
        "Ambiguity in the query": "Because the GDP is split across years, it is unclear if there needs to be additional data transformations performed to calculate summary statistics for each country before finding the highest and lowest GDP values",
        "Ambiguity resolution": "Calculate Summary statistics across all years; Generate extermes for GDP for each year",
        "Data transformations": "df.groupby('Year', "Entity")['GDP per capita'].mean(); df.groupby('Year', 'Country')["GDP"].agg(['min', 'max'])",
        "Data transformation operation": ["groupby", "summarize"],
        "New Column Name": "",
        "Derivation Specification": "",
        "Missing Data Column":""
        }

        query: What countries have the maximum and minimum agriculture contribution decade wise?
        { "query":"What countries have the maximum and minimum agriculture contribution decade wise?",
        "Relevant data columns": ["AFF value added (% of GDP)","Entity", "Year"],
        "Data column classification": ["keyword", "inferred", "inferred"],
        "Low-level visualization task": ["comparison", "find extreme"],
        "Low-level visualization task classification": ["inferred", "inferred"],
        "Visualization goal": ["exploratory"],
        "Ambiguity in the query": "There are different year ranges for across countries. it is unclear what years are to be included in the evaluation",
        "Ambiguity resolution": "Find all years that have entries for all countries and use that to calculate decades",
        "Data transformations": "cleaned_df = df.dropna(subset=['AFF value added (% of GDP)', 'GDP per capita']); valid_years = cleaned_df.groupby('Year').size(); years_with_valid_entries_for_all_countries = valid_years[valid_years == len(df['Entity'].unique())].index.tolist()
        ; df = valid_entries_df = df[df['Year'].isin(years_with_valid_entries_for_all_countries)][['Year', 'Entity', 'AFF value added (% of GDP)']]",
        "Data transformation operation": ["filter","groupby", "count", "select"],
        "New Column Name": "decade",
        "Derivation Specification": "df['Year'] = pd.to_datetime(df['Year'], format='%Y'); df['Decade'] = (df['Year'].dt.year // 10) * 10",
        "Missing Data Column":""
        }
        Analyze the following query using the instructions above
    """
    for item in tqdm(chats, desc="Processing querries"):
        messages = []
        system = system_instruction
        message = f"{item['dataset']} \n\n {item['text']}"
        print(f"{i}: {message}")
        i = i+1
        response = ""
        messages.append({"role": "user", "content": message})
        for new_text in chat_model.stream_chat(messages,system=system,top_p=0.8,top_k=50,temperature=0.70,repetition_penalty=1.2):
            response += new_text
        item['Mixtral_8x7B_output'] = response
        print(f"Assistant: {response}")
        responses.append({
            "query": item["text"],
            "response": response
        })
        print("------")
    new_file_path = 'data/nl_corpus_res.json'
    save_chat(responses, new_file_path)

    
# srun --pty \
#     --gres=gpu:rtxa4000 \
#     --cpus-per-task=8 \
#     --mem=10G \
#     --job-name=sft \
#     --qos=high \
#     --partition=tron \
#     --time=12:00:00 \
#     bash
    
if __name__ == "__main__":
    main()