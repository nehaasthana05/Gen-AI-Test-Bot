import pymongo
import sys
from pathlib import *
from time import *

# MongoDB connection URI without authentication
hostname = '130.113.68.57'  # Update to the server's IP address
port = 27017
database_name = 'genAI'

uri = f'mongodb://{hostname}:{port}/{database_name}'
client = pymongo.MongoClient(uri)

db = client[database_name]
code_modules_collection = db['Code_Modules']
test_cases_collection = db['Test_Cases']
library_dependencies_collection = db['Library_Dependencies']

# Fetch relavent functions from database
def get_code_modules(developer_id, file):
    try:
        modules = code_modules_collection.find({'developer_id': developer_id, 'file': file})
        return [module for module in modules]
    except Exception as e:
        print("Error retrieving code modules:", e)
        return []

# Fetch relavent assertions from database
def get_assertions(developer_id, file):
    try:
        assertions = test_cases_collection.find({'developer_id': developer_id, 'file': file})
        return [assertion for assertion in assertions]
    except Exception as e:
        print("Error retrieving assertions:", e)
        return []

# Search code file for functions
def split_file(filepath):
    fPath = Path(filepath)
    reader = open(filepath)
    lines = reader.readlines()
    reader.close()
    
    funcs = [] # functions
    libs = [] # libraries (dependencies)
    i = 0
    inFunc = False
    
    for line in lines:
        if line.strip().startswith("from") or line.strip().startswith("import"):
            libs.append(line.strip())
        
        #Function end
        if inFunc:  
            if line[0] not in [' ', '#', '\n', '\t'] or i == len(lines) - 1:
                inFunc = False
                func_end = i
                funcs.append({'function_name': func_name, 'begin': func_begin, 'end': func_end, 'libs': libs, 'file': fPath.name})
        i += 1
        
        # Function begin
        if (not inFunc) and line.startswith("def"):
            func_name = line[4:].split('(')[0]
            func_begin = i
            inFunc = True

    return funcs

# Reads assertion file
# Returns an array of arrays in the form [name of mapped function, assertion code, assertion id # in relation to function, result from most recent test, associated filename]
def map_assertions(funcs, filepath): # filepath refers to the test suite file.
    fPath = Path(filepath)
    reader = open(filepath)
    lines = reader.readlines()
    reader.close()
    
    assertions = []
    function_dictionary = [] # a dictionary that maps each function to the number of assertions associated with it.
    
    for func in funcs:
        function_dictionary.append([func['function_name'], 0])
        
    for line in lines:
        l = line.strip()
        if l[0:6] == "assert":
            funcName = l[7:].split('(')[0].strip()
            n = -1
            i = 0
            while i < len(funcs):
                if funcName == funcs[i]['function_name']:
                    n = function_dictionary[i][1] + 1
                    function_dictionary[i][1] = n
                    assertions.append({'function_name': funcName, 'assertion': l, 'assertion_number': n, 'result': "none", 'file': fPath.name.replace(".txt",".py")})
                    break
                i += 1
        
    return assertions

# Inserts functions into the database
def insert_code_modules(funcs, developer_id, filepath):
    for func in funcs:
        with open(filepath) as f:
            code = ''.join(f.readlines()[func['begin']:func['end']])
            try:
                code_modules_collection.delete_many({"developer_id": developer_id, "function_name": func['function_name'], "file": func['file']})
                code_modules_collection.insert_one({
                    'developer_id': developer_id,
                    'function_name': func['function_name'],
                    'code': code,
                    'file': func['file']
                })
                #print("Code module inserted:", func['function_name'])
            except Exception as e:
                print("Error inserting code module:", e)

# Inserts assertions into the database
def insert_test_cases(assertions, developer_id):
    timestamp = time()
    for assertion in assertions:
        try:
            old_data = test_cases_collection.find_one({"developer_id": developer_id, "function_name": assertion['function_name'], "file": assertion['file'], "assertion": assertion['assertion']})
            
            if old_data is None:
                history = []
            else:
                history = old_data['history']
            
            if assertion['result'] == 'pass':
                history.insert(0, True)
            elif assertion['result'] == 'fail':
                history.insert(0, False)
            
            if len(history) > 5:
                history = history[0:5]

            test_cases_collection.insert_one({
                'developer_id': developer_id,
                'function_name': assertion['function_name'],
                'assertion': assertion['assertion'],
                'assertion_number': assertion['assertion_number'],
                'file': assertion['file'],
                'timestamp': timestamp,
                'history': history
            })
        except Exception as e:
            print("Error inserting test case:", e)
    for assertion in assertions:
        test_cases_collection.delete_many({"developer_id": developer_id, "function_name": assertion['function_name'], "file": assertion['file'], "timestamp": { "$ne": timestamp }})

# Inserts libraries into the database
def insert_library_dependencies(funcs, developer_id):
    for func in funcs:
        for lib in func['libs']:
            try:
                library_dependencies_collection.delete_many({"developer_id": developer_id, "function_name": func['function_name'], "file": func['file']})
                library_dependencies_collection.insert_one({
                    'developer_id': developer_id,
                    'function_name': func['function_name'],
                    'library': lib,
                    'file': func['file']
                })
            except Exception as e:
                print("Error inserting library dependency:", e)