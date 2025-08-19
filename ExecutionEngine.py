import subprocess
import re
import os
import sys
from TestCaseGenerator import *
from Module_Splitter import *
from pathlib import *

os.environ["COLUMNS"] = "100"

# Send code and assertions to ChatGPT to expand assertions list
def fetch_tests(file, assertions, assertions_path):
    reader = open(file)
    code = reader.read()
    reader.close()
    test_suite = write_tests(code, assertions)
    writer = open(assertions_path, "w")
    writer.write(test_suite)
    writer.close()
    return

def update_tests(file, assertions, assertions_path, code_patch):
    reader = open(file)
    code = reader.read()
    reader.close()
    test_suite = write_updated_tests(code, assertions, code_patch)
    writer = open(assertions_path, "w")
    writer.write(test_suite)
    writer.close()
    return

# Core function for running tests and measurements
def run_tests(mode, path, code):
    coverage(mode, path, code)
    
    pytest_result, missing_lines, error, tests_passed, tests_failed, failed_assertions, coverage_percentage = coverage(mode, path, code)
    static_result, static_rating = static_analysis(path.joinpath(code))
    static_rating = static_rating.replace('...', '') + " / 10"
    return pytest_result, missing_lines, error, failed_assertions, coverage_percentage, static_result, static_rating

# Static analysis using pylint
def static_analysis(path):   
    python_interpreter = sys.executable

    result = subprocess.run(python_interpreter + " -m pylint " + str(path), capture_output=True, text=True, shell=True).stdout

    match = re.search(r"Your code has been rated at ([\d.]+)/10", result)
    if match:
        rating = match.group(1)
    else:
        rating = "No rating found."

    return result, rating

# Coverage metrics using coverage.py and assertion testing with pytest
def coverage(mode, path, code):
    python_interpreter = sys.executable

    pytest_result = ''; coverage_report = ''; coverage_percentage = ''; missing_lines = ''; error = ''
    tests_failed = -1; tests_passed = -1
    failed_assertions = []

    if mode == 'line':
        pytest_result = subprocess.run(python_interpreter + " -m coverage run -m pytest " + str(path), capture_output=True, text=True, shell=True).stdout
    elif mode == 'branch':
        pytest_result = subprocess.run(python_interpreter + " -m coverage run --branch -m pytest " + str(path), capture_output=True, text=True, shell=True).stdout
    else:
        print("For the first argument, select either 'line' or 'branch'")
        return pytest_result, coverage_report, coverage_percentage
    
    coverage_report = subprocess.run(python_interpreter + " -m coverage report -m", capture_output=True, text=True, shell=True).stdout


    error_pattern = r"={3,}\s*ERRORS\s*={3,}\n(.*?)\n={3,}\s*short test summary info\s*={3,}"
    error_match = re.search(error_pattern, pytest_result, re.DOTALL)
    if error_match:
        error = error_match.group(1)

    failed_assertion_pattern = r">\s*assert\s+([^\n]+?)\n(?:[^\n]*\n)*?E\s+([^\n]+)?(?:assert\s+([^\s]+)\s+==\s+([^\n]+))?"
    matches = re.finditer(failed_assertion_pattern, pytest_result, re.DOTALL) 

    for match in matches:
        print(match.group(1))
        print(match.group(2))
        print(match.group(3))
        print(match.group(4))

        expression = match.group(1)
        start = expression.find("(") + 1
        func = f"{expression[0:start-1]}"
        errorMsg = match.group(2)
        expected_result = match.group(4)
        actual_result = match.group(3)
        if expected_result is None and actual_result is None:
            actual_result = errorMsg
        failed_assertions.append([func, expression, expected_result, actual_result])

    pattern_test_summary = r"(\d+) failed, (\d+) passed"
    test_summary_match = re.search(pattern_test_summary, pytest_result)
    if test_summary_match:
        tests_failed = int(test_summary_match.group(1))
        tests_passed = int(test_summary_match.group(2))

    pattern_percentage = code + r"\s+\d+\s+\d+\s+(\d+%)\s*?([^\n]*)?\n"    
    percentage_match = re.search(pattern_percentage, coverage_report)
    if percentage_match:
        coverage_percentage = percentage_match.group(1)
        missing_lines = percentage_match.group(2).strip()
    

    return pytest_result, missing_lines, error, tests_passed, tests_failed, failed_assertions, coverage_percentage

# Compare all assertions to failed assertions
def accuracy_tracker(assertions, failedAssertions):
    new_assertions = []
    for astn in assertions:
        failed = False
        for f_astn in failedAssertions:
            # if the next failed assertion is equivalent to astn
            if (f_astn[0] == astn['function_name']) and (f_astn[1] in astn['assertion']):
                new_assertions.append({
                    'function_name': astn['function_name'], 
                    'assertion': astn['assertion'], 
                    'assertion_number': astn['assertion_number'],
                    'file': astn['file'],
                    'result': "fail"
                })
                failed = True
                break
        if failed:
            continue
        new_assertions.append({
            'function_name': astn['function_name'], 
            'assertion': astn['assertion'], 
            'assertion_number': astn['assertion_number'], 
            'file': astn['file'],
            'result': "pass"
            })
    return new_assertions

def build_test_suite(astns, srcfile):
    txt = "from " + srcfile.stem.split('test_')[1] + " import *\n"
    
    for astn in astns:
        txt += "\ndef test_" + astn['function_name'] + "_astn_" + str(astn['assertion_number']) + "():\n\t" + astn['assertion'] + "\n"
    
    file = open(srcfile, "w")
    file.write(txt)
    file.close()
    return

def get_assertion_data(assertions, failed_assertions):
    report = ""
    for assertion in assertions:
        report += "Test Case: " + assertion['assertion'] + "\n"
        if assertion['history'][0] == True:
            report += "Result: Pass\n"
        else:
            report += "Result: Fail\n"
            for failed_assertion in failed_assertions:
                if failed_assertion[0] == assertion['function_name'] and failed_assertion[1] in assertion['assertion']:
                    if failed_assertion[2] is None:
                        report += failed_assertion[3] + "\n"
                        failed_assertions.remove(failed_assertion)
                        break
                    elif failed_assertion[2] in assertion['assertion']:
                        report += "Actual Test Case Result: " + failed_assertion[3] + "\n"
                        failed_assertions.remove(failed_assertion)
                        break
        report += "History: (Last 5)\n"
        report += "- (Most Recent)\n"
        for result in assertion['history']:
            if result == True:
                report += "|\tPass\n"
            else:
                report += "|\tFail\n"
        report += "- (Least Recent)\n\n"

    return report

