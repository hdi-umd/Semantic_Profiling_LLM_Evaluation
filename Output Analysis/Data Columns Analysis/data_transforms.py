import pandas as pd
import types, json
import ast


def run_single_transform(q, caller="gt"):
    """input is a dict of { dataset:"", code:""}"""
    #retrieve the relevant data transform
    try:
        if q["dataset"] == "GunViolence.csv":
            return run_transform_gunviolence(q, caller)
        
        if q['code']=="": return 'data transforms is empty'
        path = "../../datasets/"+q["dataset"]
        code = reformat_code(q["code"],4)
        return_df = regex_extractor(reformat_code(q["code"], 0))

        #having issues with code being run that contains clustering or more sophisticated than what was asked. 
        banned_imports = ["sklearn.cluster", "matplotlib.pyplot", "pearsonr", "sklearn.covariance", "scipy", "seaborn", "scipy.stats", "scipy.spatial", "geopylib", "geohash", "statsmodels.api"]
        for i in banned_imports:
            if i in code:
                qu = q["query"]
                # print("banned import ", e)
                file = open(f"./results/{caller}_unexecuted_codes_path.txt", "a")
                file.write(f"unable to execute {caller} code for query '{qu}'. Error: {i} import found;' \n")
                file.close()
                return "Error running code"
        script = """ 
import pandas as pd
import datetime, re
import numpy as np
def transform(dataset):
    df=pd.read_csv(dataset, thousands=',')
{}
    return {}
res=transform("{}")
    """.format(code, return_df, path)
        
      
   
        my_namespace = types.SimpleNamespace()
        exec(script, my_namespace.__dict__)
        # print("res: ", my_namespace.res)
        if isinstance(my_namespace.res, pd.DataFrame):
            return json.dumps(my_namespace.res.dtypes.apply(lambda x: x.name).to_dict())
        if isinstance(my_namespace.res, pd.Series):
            d = my_namespace.res.reset_index().to_dict()
        # print(d)
            return json.dumps(
                pd.DataFrame.from_dict(d).dtypes.apply(lambda x: x.name).to_dict()
            )
        return my_namespace.res #llms seem to want to return a single value so just return this instead.
    except Exception as e:
        qu = q["query"]
        # print("error running query: ", e)
        file = open(f"./results/{caller}_unexecuted_codes_path.txt", "a")
        file.write(f"unable to execute {caller} code for query '{qu}'. Error:{e};' \n")
        file.close()
        return "Error running code"

def run_transform_gunviolence(q, caller="gt"):
    """input is a dict of { dataset:"", code:""}"""
    
    #retrieve the relevant data transform
    try:
        code = reformat_code(q["code"],4)
        return_df = regex_extractor(reformat_code(q["code"], 0))

        #having issues with code being run that contains clustering or more sophisticated than what was asked. 
        banned_imports = ["sklearn.cluster", "matplotlib.pyplot", "pearsonr", "sklearn.covariance", "scipy", "seaborn", "scipy.stats", "scipy.spatial", "geopylib", "geohash", "statsmodels.api"]
        for i in banned_imports:
            if i in code:
                qu = q["query"]
                # print("banned import ", e)
                file = open(f"./results/{caller}_unexecuted_codes_path.txt", "a")
                file.write(f"unable to execute {caller} code for query '{qu}'. Error: {i} import found;' \n")
                file.close()
                return "Error running code"
        #TODO: Ensure zip file is uncompressed to make sure code actually runs
        script = """ 
import pandas as pd
import datetime, re
import numpy as np
def transform():
    df1=pd.read_csv("../../datasets/gun violence datasets/data.world_gun_death_in_america.csv", thousands=',')
    df2=pd.read_csv("../../datasets/gun violence datasets/firearm_deaths_usafacts.csv", thousands=',')
    df3=pd.read_csv("../../datasets/gun violence datasets/gun-violence-data_01-2013_03-2018.csv", thousands=',')
    df = pd.concat([df1, df2, df3], axis=1)
    
{}
    return {}
res=transform()
    """.format(code, return_df)
        
   
        my_namespace = types.SimpleNamespace()
        exec(script, my_namespace.__dict__)
        # print(my_namespace.res)
        if isinstance(my_namespace.res, pd.DataFrame):
            return json.dumps(my_namespace.res.dtypes.apply(lambda x: x.name).to_dict())
        if isinstance(my_namespace.res, pd.Series):
            d = my_namespace.res.reset_index().to_dict()
        # print(d)
            return json.dumps(
                pd.DataFrame.from_dict(d).dtypes.apply(lambda x: x.name).to_dict()
            )
        return my_namespace.res #llms seem to want to return a single value so just return this instead.
    except Exception as e:
        qu = q["query"]
        # print(e)
        file = open(f"./results/{caller}_unexecuted_codes_path.txt", "a")
        file.write(f"unable to execute {caller} code for query '{qu}'. Error:{e};' \n")
        file.close()
        return "Error running code"    

def regex_extractor(code):
    """finds and extracts the last variable in the code snippet so we know what to return in
    transform function"""
    # pattern = r'\b(\w+)\s*=\s*(.+?)\n'

    # # Find all variable assignments using regex
    # variable_assignments = re.findall(pattern, code)
    # print("output", variable_assignments)
    # return variable_assignments[-1][0] if len(variable_assignments)>0 else "df"
    # Parse the Python code into an abstract syntax tree
    
    tree = ast.parse(code)

# Function to recursively extract variable assignments
    def extract_assignments(node):
        assignments = []
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_name = target.id
                    # value = ast.dump(node.value)
                    # assignments.append((variable_name, value))
                    assignments.append(variable_name)
        for child_node in ast.iter_child_nodes(node):
            assignments.extend(extract_assignments(child_node))
        return assignments
    
    #first check if there is an assignment already. If so return the last variable assignment
    out = extract_assignments(tree)
    if len(out)>0:
        return out[-1]
    
    #if no assignment then check for function calls then return the last line of code in code instead
    return code.splitlines()[-1]


def has_function_call(tree):
    """use this to check if a function is called in the transforms """
    # Parse the code string into an AST
    # tree = ast.parse(code_str)
    
    # Define a custom visitor to traverse the AST
    class FunctionCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_function_call = False
            
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                # Check if the call is an attribute call (e.g., obj.method())
                # In this case, we're interested in the attribute part (method)
                if isinstance(node.func.value, ast.Name):
                    # Check if the attribute is a function call (i.e., it's an attribute of a name)
                    self.has_function_call = True
            self.generic_visit(node)
    
    # Visit the AST with the custom visitor
    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    
    # Return whether a function call was found
    return visitor.has_function_call


def reformat_code(code, indentation):
    """reformat code to maintain python indentation"""
    
    # Split the code string by ";"
    lines = code.split(';')

    # Reformat each line to ensure valid Python indentation
    formatted_lines = []
    current_indentation = indentation
    for line in lines:
        line = line.strip()
        if line:
            if line.endswith(':'):
                formatted_lines.append(' ' * current_indentation + line)
                current_indentation += 4
            elif line.startswith('elif') or line.startswith('else:') or line.startswith('except:') or line.startswith('finally:'):
                current_indentation -= 4
                formatted_lines.append(' ' * current_indentation + line)
                current_indentation += 4
            else:
                formatted_lines.append(' ' * current_indentation + line)

    # Join the formatted lines with newline characters
    formatted_code = '\n'.join(formatted_lines)
    return formatted_code

if __name__=="__main__":
    code = {
        "query":"Is one sex more likely to perpetrate gun violence",
        "code": "df[(df[\"Market_value\"]==50000000)&(df[\"Transfer_fee\"]==58000000)]",
        "dataset": "top250-00-19.csv"
    }
    print(run_single_transform(code, "test"))