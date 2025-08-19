from Module_Splitter import *
from ExecutionEngine import *
from pathlib import *

file_path = Path(sys.argv[1])
assertions_path = Path(sys.argv[2])
code_patch = str(sys.argv[3])
dev_id = sys.argv[4]

print(code_patch)

functions = split_file(file_path)
assertions = map_assertions(functions, assertions_path)
if len(assertions) < 3:
    raise Exception

update_tests(file_path, assertions, assertions_path, code_patch)
assertions = map_assertions(functions, assertions_path)

writer = open(assertions_path, 'w')
writer.write("")
writer.close

writer = open(assertions_path, 'a')
for assertion in assertions:
    writer.write(assertion['assertion'] + '\n')
writer.close()
insert_code_modules(functions, dev_id, file_path)
insert_library_dependencies(functions, dev_id)
insert_test_cases(assertions, dev_id)
