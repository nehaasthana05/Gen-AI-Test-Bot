import pymongo
import os
from ExecutionEngine import *
from Module_Splitter import *
from pathlib import *

file_path = Path(sys.argv[1])
assertions_path = Path(sys.argv[2])
dev_id = sys.argv[3]
functions = split_file(file_path)
assertions = map_assertions(functions, assertions_path)
src_path = file_path.parent
src_code = file_path.name
test_suite = "test_" + src_code
test_path = src_path.joinpath(test_suite)

#Connect to server
hostname = '130.113.68.57'  # Update to the server's IP address
port = 27017
database_name = 'genAI'

uri = f'mongodb://{hostname}:{port}/{database_name}'
client = pymongo.MongoClient(uri)
db = client[database_name]
results_collection = db['Results']

# Run tests
insert_code_modules(functions, dev_id, file_path)
insert_library_dependencies(functions, dev_id)
build_test_suite(assertions, test_path)
pytest_result, missing_lines, error, failed_assertions, coverage_percentage, static_result, static_rating = run_tests('line', src_path, src_code)
os.remove(test_path)

if error != '':
    print("There was an error!\n" + error)
    raise Exception

# Update assertions
new_assertions = accuracy_tracker(assertions, failed_assertions)
insert_test_cases(new_assertions, dev_id)

# Report data
assertions = get_assertions(dev_id, src_code)
functions = get_code_modules(dev_id, src_code)
total_tests = len(assertions)
tests_failed = len(failed_assertions)
tests_passed = total_tests - tests_failed
accuracy_rate = int((tests_passed / total_tests) * 100)
accuracy = str(tests_passed) + " / " + str(total_tests) + " (" + str(accuracy_rate) + "%)"
assertion_results = get_assertion_data(assertions, failed_assertions)

print("-----Accuracy-----")
print(accuracy)
print("-----Coverage Rating-----")
print(coverage_percentage)
print("-----Lines Not Covered-----")
print(missing_lines)
print("-----Code Rating-----")
print(static_rating)
print("-----Test Case Results-----")
print(assertion_results)
print("-----Static Analyisis Report-----")
print(static_result)

results_collection.delete_many({'developer_id': dev_id})
results_collection.insert_one({
    'developer_id': dev_id,
    'accuracy': accuracy,
    'coverage_rating': coverage_percentage,
    'static_rating': static_rating,
    'assertion_results': assertion_results,
    'missing_lines': missing_lines,
    'static_report': static_result
})