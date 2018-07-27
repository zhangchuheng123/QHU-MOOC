import json
import hashlib
import numpy as np
import pandas as pd
from os import makedirs
from os import listdir
from os.path import join as joindir
import re 

def process_test_case(path, spj=False):
    size_cache = {}
    md5_cache = {}
        
    test_case_list = listdir(path)
    test_case_list = sorted([item for item in test_case_list if item[-2:] == 'in' or item[-3:] == 'out'])
    
    for item in test_case_list:
        with open(joindir(path, item), 'r+b') as f:
            content = f.read().replace(b'\r\n', b'\n')
            size_cache[item] = len(content)
            if item.endswith('.out'):
                md5_cache[item] = hashlib.md5(content.rstrip()).hexdigest()
            f.seek(0)
            f.write(content)
            f.truncate()
    
    test_case_info = {'spj': spj, 'test_cases': {}}
    
    info = []

    if spj:
        for index, item in enumerate(test_case_list):
            data = {'input_name': item, 'input_size': size_cache[item]}
            info.append(data)
            test_case_info['test_cases'][str(index + 1)] = data
    else:
        # ["1.in", "1.out", "2.in", "2.out"] => [("1.in", "1.out"), ("2.in", "2.out")]
        test_case_list = zip(*[test_case_list[i::2] for i in range(2)])
        for index, item in enumerate(test_case_list):
            data = {"stripped_output_md5": md5_cache[item[1]],
                    "input_size": size_cache[item[0]],
                    "output_size": size_cache[item[1]],
                    "input_name": item[0],
                    "output_name": item[1]}
            info.append(data)
            test_case_info["test_cases"][str(index + 1)] = data

    with open(joindir(path, 'info'), "w", encoding="utf-8") as f:
        f.write(json.dumps(test_case_info, indent=4))
        
    return test_case_info

np.random.seed(1234)

sample_template = """
#include <stdio.h>

int main()
{
    int a,b;
    scanf("%d %d",&a, &b);
    printf("%d\n",a+b);
    return 0;
}
"""

# Generate example problems
problem_path = 'data/problems'
makedirs(problem_path, exist_ok=True)

# Choice
problem = pd.DataFrame()
for i in range(100):
    problem.loc[i, 'id'] = i
    problem.loc[i, 'description'] = hashlib.md5(str(i).encode('utf-8')).hexdigest()
    problem.loc[i, 'A'] = hashlib.md5('A{}'.format(i).encode('utf-8')).hexdigest()[:10]
    problem.loc[i, 'B'] = hashlib.md5('B{}'.format(i).encode('utf-8')).hexdigest()[:10]
    problem.loc[i, 'C'] = hashlib.md5('C{}'.format(i).encode('utf-8')).hexdigest()[:10]
    problem.loc[i, 'D'] = hashlib.md5('D{}'.format(i).encode('utf-8')).hexdigest()[:10]
    problem.loc[i, 'answer'] = np.random.choice(list('ABCD'))
    problem.loc[i, 'tag'] = np.random.choice(['C_class', 'Cpp_class'])
problem['id'] = problem['id'].astype(int)
problem.to_csv(joindir(problem_path, 'Choice.csv'))

# Completion
problem = pd.DataFrame()
for i in range(100):
    problem.loc[i, 'id'] = i
    problem.loc[i, 'description'] = \
        hashlib.md5(str(i).encode('utf-8')).hexdigest() + ' ____ ' + hashlib.md5(str(i).encode('utf-8')).hexdigest()
    problem.loc[i, 'answer'] = hashlib.md5(str(i).encode('utf-8')).hexdigest()[:5]
    problem.loc[i, 'tag'] = np.random.choice(['C_class', 'Cpp_class'])
problem['id'] = problem['id'].astype(int)
problem.to_csv(joindir(problem_path, 'Completion.csv'))

# TrueOrFalse
problem = pd.DataFrame()
for i in range(100):
    problem.loc[i, 'id'] = i
    problem.loc[i, 'description'] = hashlib.md5(str(i).encode('utf-8')).hexdigest()
    problem.loc[i, 'answer'] = np.random.choice(['T', 'F'])
    problem.loc[i, 'tag'] = np.random.choice(['C_class', 'Cpp_class'])
problem['id'] = problem['id'].astype(int)
problem.to_csv(joindir(problem_path, 'TrueOrFalse.csv'))

# ProgramCorrection
problem = pd.DataFrame()
for i in range(100):
    problem.loc[i, 'id'] = i
    problem.loc[i, 'description'] = hashlib.md5(str(i).encode('utf-8')).hexdigest()
    problem.loc[i, 'template'] = sample_template
    problem.loc[i, 'test_case_id'] = '1000'
    problem.loc[i, 'tag'] = np.random.choice(['C_class', 'Cpp_class'])
problem['id'] = problem['id'].astype(int)
problem.to_csv(joindir(problem_path, 'ProgramCorrection.csv'))

# ProgramReading
problem = pd.DataFrame()
for i in range(100):
    problem.loc[i, 'id'] = i
    problem.loc[i, 'description'] = hashlib.md5(str(i).encode('utf-8')).hexdigest() + '\n' + sample_template
    problem.loc[i, 'answer'] = hashlib.md5(str(i).encode('utf-8')).hexdigest()[:5]
    problem.loc[i, 'tag'] = np.random.choice(['C_class', 'Cpp_class'])
problem['id'] = problem['id'].astype(int)
problem.to_csv(joindir(problem_path, 'ProgramReading.csv'))

# ProgramDesign
problem = pd.DataFrame()
for i in range(100):
    problem.loc[i, 'id'] = i
    problem.loc[i, 'description'] = hashlib.md5(str(i).encode('utf-8')).hexdigest() + '\n' + sample_template
    problem.loc[i, 'test_case_id'] = '1000'
    problem.loc[i, 'tag'] = np.random.choice(['C_class', 'Cpp_class'])
problem['id'] = problem['id'].astype(int)
problem.to_csv(joindir(problem_path, 'ProgramDesign.csv'))

# Generate user adding folder
users_path = 'data/users'
makedirs(users_path, exist_ok=True)
users = pd.DataFrame()
for i in range(100):
    users.loc[i, 'username'] = 2016311001 + i
    users.loc[i, 'password'] = 2016311001 + i
    users.loc[i, 'usertype'] = 1
    users.loc[i, 'classes'] = np.random.choice(['C_class', 'Cpp_class'])
users['username'] = users['username'].astype(str)
users['password'] = users['password'].astype(str)
users['usertype'] = users['usertype'].astype(int)
users.to_csv(joindir(users_path, 'add_users.csv'))

# Generate test_case: A+B problem
tc_path = 'data/test_case/1000'
makedirs(tc_path, exist_ok=True)
for i in [1, 2, 3]:
    with open(joindir(tc_path, '{}.in'.format(i)), 'w') as f:
        a = np.random.randint(20) - 10
        b = np.random.randint(20) - 10
        f.write('{} {}'.format(a, b))
    with open(joindir(tc_path, '{}.out'.format(i)), 'w') as f: 
        f.write('{}'.format(a + b))
process_test_case(tc_path)

# Generate exam
exams_path = 'data/exams'
makedirs(exams_path, exist_ok=True)

exam1 = {
    'name': '第一次测试',
    'num_choice': 10,
    'point_choice': 1,
    'tag_choice': 'C_class',
    'num_completion': 10,
    'point_completion': 1,
    'tag_completion': 'C_class',
    'num_trueorfalse': 10,
    'point_trueorfalse': 1,
    'tag_trueorfalse': 'C_class',
    'num_programcorrection': 2,
    'point_programcorrection': 5,
    'tag_programcorrection': 'C_class',
    'num_programreading': 2,
    'point_programreading': 5,
    'tag_programreading': 'C_class',
    'num_programdesign': 2,
    'point_programdesign': 25,
    'tag_programdesign': 'C_class',
    'classes': 'C_class'
}

with open(joindir(exams_path, 'exam_test.json'), 'w') as f:
    f.write(json.dumps(exam1, indent=4))
