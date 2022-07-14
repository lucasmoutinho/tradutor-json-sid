testcases = []

# name should match the directory name

# Main testcase that covers most of the functionality
# mode = a2b
# datagrids with renaming
# merging with level1 and level2
# merge whole datagrid in level1
# insert whole datagrid as root param
# transform request message
# dummy datagrid for wrong extracting rule
# insert data parameters to root
testcases.append({'name': 'main', 'status': True, 'errorMsg': None})

# wrong mode
testcases.append({'name': 'mode_wrong', 'status': False, 'errorMsg': 'mode WRONG is not allowed'})

# mode = b2a
# with transformation
testcases.append({'name': 'b2a_transform_ok', 'status': True, 'errorMsg': None})

# mode = b2a
# transformation failed
testcases.append({'name': 'b2a_transform_fail', 'status': False, 'errorMsg': 'Error occured while creating dest'})

# mode = a2custom
testcases.append({'name': 'a2custom', 'status': True, 'errorMsg': None})

# No extract rule
# Take all new data
testcases.append({'name': 'no_extract_rule', 'status': True, 'errorMsg': None})

# Wrong transform rule
# Test exception during processing params
testcases.append({'name': 'transform_rule_fail', 'status': False, 'errorMsg': 'Error occured while creating all_data'})

# mode = a2a
testcases.append({'name': 'a2a', 'status': True, 'errorMsg': None})

# Fail validate srcData
testcases.append({'name': 'validate_srcData_fail', 'status': False, 'errorMsg': 'Source data failed validation'})

# Error validate srcData
testcases.append({'name': 'validate_srcData_error', 'status': False, 'errorMsg': 'Error occured while validation'})