from .languages import c_lang_config, cpp_lang_config, java_lang_config, c_lang_spj_config, \
    c_lang_spj_compile, py2_lang_config, py3_lang_config
from .client import JudgeServerClient
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from backend.forms import LoginForm, MyPasswordChangeForm
from backend.models import MyUser, ExamResult, Exam, Problem
from os import remove as dangerousremove
from os.path import join as joindir
from os.path import isfile
from os.path import isdir
from os import listdir
import numpy as np
import pandas as pd
import hashlib
import json
import csv
import pdb
import re

token = "QHU_ADMIN_TOKEN"
problem_types = ['choice', 'completion', 'true_or_false', 'program_correction', 'program_reading', 'program_design']
problem_files = ['Choice.csv', 'Completion.csv', 'TrueOrFalse.csv', 'ProgramCorrection.csv', 'ProgramReading.csv', 'ProgramDesign.csv']

def index(request):
    check_new_users(request)
    check_test_cases(request)
    check_exams(request)
    check_problem_base(request)
    return render(request, 'index.html')

def check_new_users(request):
    path = 'data/users/add_users.csv'
    if isfile(path):
        data = pd.read_csv(path, index_col=0)
        for i in range(data.shape[0]):
            username = str(int(data.loc[i, 'username']))
            password = str(int(data.loc[i, 'password']))
            usertype = int(data.loc[i, 'usertype'])
            is_staff = 1 if usertype == 2 else 0
            classes = str(data.loc[i, 'classes'])
            if len(User.objects.filter(username=username)) == 0:
                user = User.objects.create_user(username=username, password=password, is_staff=is_staff)
                user.save()
                myuser = MyUser(user=user, usertype=usertype, classes=classes)
                myuser.save()
        dangerousremove(path)
        messages.success(request, '成功更新用户名单，添加用户数目：{}'.format(data.shape[0]))

def check_test_cases(request):
    """
    如果有新增测试点但是没有生存相应的info文件，那么就生产相应的文件
    """
    path = 'data/test_case/'
    count = 0
    test_cases = listdir(path)
    for t in test_cases:
        if isdir(joindir(path, t)):
            if not isfile(joindir(path, t, 'info')):
                process_test_case(joindir(path, t))
                count += 1
    if count > 0:
        messages.success(request, '成功生成{}个测试点info'.format(count))

def check_exams(request):
    path = 'data/exams'

    exam_list = listdir(path)
    exam_list = [item for item in exam_list if re.match('.*\.json', item)]

    count = 0
    for exam in exam_list:
        eid = exam[:-5]
        exam_ress = Exam.objects.filter(eid=eid)
        if len(exam_ress) == 0:
            count += 1
            with open(joindir(path, exam), 'r') as f:
                exam_json = json.load(f)
                exam_json['eid'] = exam.replace('.json', '')
                exam_obj = Exam(**exam_json)
                exam_obj.save()
        dangerousremove(joindir(path, exam))
    if count > 0:
        messages.success(request, '成功添加{}个考试'.format(count))

def check_problem_base(request):
    converters = [
        {'id': int, 'description': str, 'A': str, 'B': str, 'C': str, 'D': str, 'answer': str, 'tag': str},
        {'id': int, 'description': str, 'answer': str, 'tag': str},
        {'id': int, 'description': str, 'answer': str, 'tag': str},
        {'id': int, 'description': str, 'template': str, 'test_case_id': str, 'tag': str},
        {'id': int, 'description': str, 'answer': str, 'tag': str},
        {'id': int, 'description': str, 'test_case_id': str, 'tag': str},
    ]
    path = 'data/problems'
    counter = 0
    for count, file in enumerate(problem_files):
        if not isfile(joindir(path, file)):
            continue
        data = pd.read_csv(joindir(path, file), index_col=0, converters=converters[count])
        data.rename(columns={'id': 'pid', 'A': 'choice_A', 'B': 'choice_B', 'C': 'choice_C', 'D': 'choice_D'}, inplace=True)
        data['problem_type'] = count
        dlist = data.to_dict('record')
        for d in dlist:
            problem_ress = Problem.objects.filter(pid=d['pid'], problem_type=d['problem_type'])
            if len(problem_ress) == 0:
                problem = Problem(**d)
                problem.save()
                counter += 1
        dangerousremove(joindir(path, file))
    if counter > 0:
        messages.success(request, '成功添加{}个试题'.format(counter))

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

def login(request):
    # When already logged in
    if request.user.is_authenticated:
        messages.warning(request, '用户 {username}, 你已经登陆'.format(username=request.user.username))
        return redirect('index')
    
    # Attempt to login 
    login_form = LoginForm(request.POST.dict() or None)
    if request.method == 'POST' and login_form.is_valid():
        username = login_form.cleaned_data.get('username')
        password = login_form.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, '欢迎回来, {username}'.format(username=request.user.username))
            return redirect('index')
        else:
            messages.error(request, '账号或密码错误')
    return render(request, 'login.html', {'login_form': login_form})

@login_required
def logout(request):
    messages.success(request, '登出成功, Bye~')
    auth.logout(request)
    return redirect('index')

@login_required
def changepassword(request):
    if request.method == 'POST':
        form = MyPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = MyPasswordChangeForm(request.user)
    return render(request, 'changepassword.html', {'form': form})

@login_required
def examlist(request):
    """
    显示考试列表，显示考试班级和用户班级相同的考试，并且装到dict里面传递给render
    """
    # get user's classes id
    if request.user.is_staff:
        # represent match any classes
        user_classes = None
    else:
        user_classes = request.user.myuser.classes

    if user_classes is None:
        # 显示所有考试
        exams = Exam.objects.all()
    else:
        exams = Exam.objects.filter(classes=user_classes)

    exam_list = [{'name': j.name, 'id': j.eid} for j in exams]
    
    return render(request, 'examlist.html', {'exam_list': exam_list})

@login_required
def exam(request):
    
    if request.method == 'GET':
        # >>>> 生成并且载入试题 <<<<
        
        data = {
            'choice': [],
            'completion': [],
            'true_or_false': [],
            'program_correction': [],
            'program_reading': [],
            'program_design': [],
        }

        # 该用户是否有此次考试的权限
        permission_flag = False
        if 'id' in request.GET:
            exam_id = request.GET['id']

            # get user's classes id
            if request.user.is_staff:
                # represent match any classes
                user_classes = None
            else:
                user_classes = request.user.myuser.classes
            
            user_name = request.user.username
            exams = Exam.objects.filter(eid=exam_id)
            if len(exams) > 0:
                if (user_classes is not None) and (exams[0].classes != user_classes):
                    messages.error(request, '您不能参加此次考试')
                else:
                    exam_ress = ExamResult.objects.filter(username=user_name, examname=exam_id)
                    if (len(exam_ress) > 0) and (user_classes is not None) and (exam_ress[0].is_submitted == 1):
                        messages.success(request, '您已经完成此次考试')
                        data = exam_ress[0].data.copy()
                        data.update({'score': exam_ress[0].score})
                        return render(request, 'exam_submit.html', data)
                    else:
                        permission_flag = True
            else:
                messages.error(request, '考试{}不存在'.format(exam_id))
        else:
            messages.error(request, '请在考试列表中选择您要参加的考试')

        if permission_flag:
            if len(exam_ress) > 0:
                # 如果非首次登陆，载入该用户此次考试的题目
                data = exam_ress[0].data
            else:
                # 如果首次登陆，生成考试题目，并存下该用户此次考试的题目
                data = generate_exam(exams[0])
                exam_res = ExamResult(username=user_name, examname=exam_id, 
                    data=data, is_submitted=0, exam=exams[0])
                exam_res.save()

        return render(request, 'exam.html', process_for_render(data))
    
    elif request.method == 'POST':
        
        # >>>> 保存试题或者提交判分 <<<<
        # 样例 request.post = <QueryDict: {'2_A': ['on'], 'save': ['']}>
        
        exam_id = request.GET['id']
        user_name = request.user.username

        if 'save' in request.POST:
            # 保存结果
            exam_res = ExamResult.objects.get(username=user_name, examname=exam_id)
            exam_res.data = post_to_answers(exam_res.data, request.POST)
            exam_res.save()

            messages.success(request, '保存成功')

            return render(request, 'exam.html', process_for_render(exam_res.data))

        elif 'submit' in request.POST:
            # 提交并且判分
            exam_res = ExamResult.objects.get(username=user_name, examname=exam_id)
            exam_res.data = post_to_answers(exam_res.data, request.POST)
            exam_res.data = score_answers(exam_res.data)
            exam_res.score = generate_total_score(exam_res.data)
            exam_res.is_submitted = 1
            exam_res.save()

            messages.success(request, '提交成功')

            data = exam_res.data.copy()
            data.update({'score': exam_res.score})

            return render(request, 'exam_submit.html', process_for_render(data))

def generate_exam(exam):

    data = {
        'choice': [],
        'completion': [],
        'true_or_false': [],
        'program_correction': [],
        'program_reading': [],
        'program_design': [],
    }

    # 选择题
    problems = Problem.objects.filter(problem_type=0, tag=exam.tag_choice).order_by('?')[:exam.num_choice]
    for problem in problems:
        data['choice'].append({
            'id': problem.pid,
            'description': problem.description,
            'A': problem.choice_A,
            'B': problem.choice_B,
            'C': problem.choice_C,
            'D': problem.choice_D,
            'standard_answer': problem.answer,
            'answer': 'N',
            'full_score': float(exam.point_choice),
            'score': 0
        })

    # 填空题
    problems = Problem.objects.filter(problem_type=1, tag=exam.tag_completion).order_by('?')[:exam.num_completion]
    for problem in problems:
        data['completion'].append({
            'id': problem.pid,
            'description': problem.description,
            'standard_answer': problem.answer,
            'answer': '',
            'full_score': float(exam.point_completion),
            'score': 0,
        })

    # 判断题
    problems = Problem.objects.filter(problem_type=2, tag=exam.tag_trueorfalse).order_by('?')[:exam.num_trueorfalse]
    for problem in problems:
        data['true_or_false'].append({
            'id': problem.pid,
            'description': problem.description,
            'standard_answer': problem.answer,
            'answer': 'N',
            'full_score': float(exam.point_trueorfalse),
            'score': 0,
        })

    # 程序改错题
    problems = Problem.objects.filter(problem_type=3, tag=exam.tag_programcorrection).order_by('?')[:exam.num_programcorrection]
    for problem in problems:
        data['program_correction'].append({
            'id': problem.pid,
            'description': problem.description,
            'test_case_id': problem.test_case_id,
            'full_score': float(exam.point_programcorrection),
            'source_code': problem.template,
            'score': 0,
        })

    # 程序阅读题
    problems = Problem.objects.filter(problem_type=4, tag=exam.tag_programreading).order_by('?')[:exam.num_programreading]
    for problem in problems:
        data['program_reading'].append({
            'id': problem.pid,
            'description': problem.description,
            'standard_answer': problem.answer,
            'answer': '',
            'full_score': float(exam.point_programreading),
            'score': 0,
        })

    # 程序设计题
    problems = Problem.objects.filter(problem_type=5, tag=exam.tag_programdesign).order_by('?')[:exam.num_programdesign]
    for problem in problems:
        data['program_design'].append({
            'id': problem.pid,
            'description': problem.description,
            'test_case_id': problem.test_case_id,
            'source_code': 'start your code here ...',
            'full_score': float(exam.point_programdesign),
            'score': 0,
        })

    return data
    
def process_for_render(data):
    """
    供模板渲染的 data 格式
    """
    total_num_problems = np.sum([len(data[item]) for item in problem_types])
    data.update({'total_num_problems': total_num_problems})
        
    return data

def post_to_answers(data, post):
    """
    把 request.post 转化为 data 的格式
    post 格式
        <QueryDict: {'choice_1': ['B'], 'choice_2': ['A']}>
    data 格式
        {'choice': [{'id': 1, 'answer': 'A', 'standard_answer': 'B', 'score':  5}, ...]}
    """

    # 抽取选择题答案
    for item in data['choice']:
        if 'choice_{}'.format(item['id']) in post:
            item['answer'] = post['choice_{}'.format(item['id'])]

    # 抽取填空题答案
    for item in data['completion']:
        if 'completion_{}'.format(item['id']) in post:
            item['answer'] = post['completion_{}'.format(item['id'])]

    # 抽取判断题答案
    for item in data['true_or_false']:
        if 'trueorfalse_{}'.format(item['id']) in post:
            item['answer'] = post['trueorfalse_{}'.format(item['id'])]

    # 抽取程序改错题答案
    for item in data['program_correction']:
        if 'programcorrection_{}'.format(item['id']) in post:
            item['source_code'] = post['programcorrection_{}'.format(item['id'])]

    # 抽取程序阅读题答案
    for item in data['program_reading']:
        if 'programreading_{}'.format(item['id']) in post:
            item['answer'] = post['programreading_{}'.format(item['id'])]

    # 抽取程序设计题答案
    for item in data['program_design']:
        if 'programdesign_{}'.format(item['id']) in post:
            item['source_code'] = post['programdesign_{}'.format(item['id'])]
            
    return data

def score_answers(data):
    """
    对于答案进行评分
    data 格式
        {'choice': [{'id': 1, 'score': 5, 'answer': 'A', 'standard_answer': 'B'}, {'id': 4, 'score': 5}, ...],
         'program_design': [{'id': 1, 'socre': 10, 'result_code': [0, 0, 0], 'result_infostr': 'xxx'}, ...]}
    """

    client = JudgeServerClient(token=token, server_base_url="http://127.0.0.1:12358")

    # 对选择题进行评分
    for item in data['choice']:
        if item['standard_answer'] == item['answer']:
            item['score'] = item['full_score']
        else:
            item['score'] = 0

    # 对填空题进行评分
    for item in data['completion']:
        if str(item['standard_answer']).strip() == str(item['answer']).strip():
            item['score'] = item['full_score']
        else:
            item['score'] = 0

    # 对判断题进行评分
    for item in data['true_or_false']:
        if item['standard_answer'].upper() == item['answer']:
            item['score'] = item['full_score']
        else:
            item['score'] = 0

    # 对程序改错题进行评分
    for item in data['program_correction']:
        res = client.judge(src=item['source_code'], 
            language_config=c_lang_config, max_cpu_time=1000, max_memory=1024 * 1024 * 128,
            test_case_id=item['test_case_id'], output=True)
        if res['err'] is None:
            # 程序可以正常运行
            item['result_code'] = [r['result'] for r in res['data']]
            ac_num = sum([i == 0 for i in item['result_code']])
            item['score'] = item['full_score'] / len(res['data']) * ac_num
            item['result_infostr'] = ' '.join(['testcase:{}'.format(result_code_decode(r['result'])) for r in res['data']])
        else:
            item['result_code'] = res['err']
            item['score'] = 0
            item['result_infostr'] = error_decode(res['err']) if type(res['err']) == int else res['err']

    # 对程序阅读题进行评分
    for item in data['program_reading']:
        if str(item['standard_answer']).strip() == str(item['answer']).strip():
            item['score'] = item['full_score']
        else:
            item['score'] = 0

    # 对程序设计题进行评分
    for item in data['program_design']:
        res = client.judge(src=item['source_code'], 
            language_config=c_lang_config, max_cpu_time=1000, max_memory=1024 * 1024 * 128,
            test_case_id=item['test_case_id'], output=True)
        if res['err'] is None:
            # 程序可以正常运行
            item['result_code'] = [r['result'] for r in res['data']]
            ac_num = sum([i == 0 for i in item['result_code']])
            item['score'] = item['full_score'] / len(res['data']) * ac_num
            item['result_infostr'] = ' '.join(['testcase:{}'.format(result_code_decode(r['result'])) for r in res['data']])
        else:
            item['result_code'] = res['err']
            item['score'] = 0
            item['result_infostr'] = error_decode(res['err']) if type(res['err']) == int else res['err']

    return data

def generate_total_score(data):
    """
    把分数汇总得到总分
    """
    score = 0

    for problem in problem_types:
        for item in data[problem]:
            score += item['score']

    return score

@login_required
def showall(request):
    data = {
        'result': []
    }
    if request.user.is_staff:
        results = ExamResult.objects.all()
        for result in results:
            tmp = result.data
            detail_score = { problem: np.sum([item['score'] for item in tmp[problem]]) for problem in problem_types}
            detail_score.update({
                'username': result.username,
                'examname': result.examname,
                'score': float(result.score),
            })
            data['result'].append(detail_score)
    else:
        messages.error(request, '访问此页面需要管理员权限')
        return redirect('index')
    return render(request, 'showall.html', data)

@login_required
def downloadscores(request):
    if request.user.is_staff:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="scores.csv"'
        results = ExamResult.objects.all()
        writer = csv.writer(response)
        writer.writerow(['用户名', '考试名', '总分', '选择题得分', '填空题得分', 
                         '判断题得分', '程序改错题得分', '程序阅读题得分', '程序设计题得分'])
        for result in results:
            tmp = result.data
            detail_score = { problem: np.sum([item['score'] for item in tmp[problem]]) for problem in problem_types}
            writer.writerow([result.username, result.examname, float(result.score), 
                detail_score['choice'], detail_score['completion'], detail_score['true_or_false'],
                detail_score['program_correction'], detail_score['program_reading'],
                detail_score['program_design']])
        return response
    else:
        messages.error(request, '访问此页面需要管理员权限')
        return redirect('index')
        
def result_code_decode(code):
    """
    把返回的 result_code 翻译为结果
    参考：https://docs.onlinejudge.me/#/judgeserver/api
    """
    if code == -1:
        return 'WRONG_ANSWER'
    elif code == 0:
        return 'ACCEPTED'
    elif code == 1:
        return 'CPU_TIME_LIMIT_EXCEEDED'
    elif code == 2:
        return 'REAL_TIME_LIMIT_EXCEEDED'
    elif code == 3:
        return 'MEMORY_LIMIT_EXCEEDED'
    elif code == 4:
        return 'RUNTIME_ERROR'
    elif code == 5:
        return 'SYSTEM_ERROR'
    else:
        return 'UNKNOWN_ERROR'
    
def error_decode(code):
    """
    把返回的 err 翻译为结果
    参考：https://docs.onlinejudge.me/#/judgeserver/api
    """
    if code == 0:
        return 'SUCCESS'
    elif code == -1:
        return 'INVALID_CONFIG'
    elif code == -2:
        return 'CLONE_FAILED'
    elif code == -3:
        return 'PTHREAD_FAILED'
    elif code == -4:
        return 'WAIT_FAILED'
    elif code == -5:
        return 'ROOT_REQUIRED'
    elif code == -6:
        return 'LOAD_SECCOMP_FAILED'
    elif code == -7:
        return 'SETRLIMIT_FAILED'
    elif code == -8:
        return 'DUP2_FAILED'
    elif code == -9:
        return 'SETUID_FAILED'
    elif code == -10:
        return 'EXECVE_FAILED'
    elif code == -11:
        return 'SPJ_ERROR'
    else:
        return 'UNKNOWN_ERROR'

def _load_problem_legency(path, converters, tag, num):
    data = pd.read_csv(path, index_col=0, converters=converters)
    data = data.loc[data.tag == tag]
    id_list = data['id'].tolist()
    selected_id_list = np.random.choice(id_list, size=num, replace=False)
    data = data.loc[data['id'].apply(lambda x: x in selected_id_list)].reset_index()
    return data

def load_problem_base_legency(exam_json):
    """
    载入题库并且根据exam_json来生成一套试卷
    返回的是该套试卷的一个dict，分别是每种题型的DataFrame
    """
    path = 'data/problems'
    
    # 选择题
    data_ch = _load_problem(
        path=joindir(path, 'Choice.csv'), 
        converters={'id': int, 'description': str, 'A': str, 'B': str, 'C': str, 'D': str, 'answer': str, 'tag': str},
        tag=exam_json['tag_choice'], num=exam_json['num_choice'])

    # 填空题
    data_cp = _load_problem(
        path=joindir(path, 'Completion.csv'), 
        converters={'id': int, 'description': str, 'answer': str, 'tag': str},
        tag=exam_json['tag_completion'], num=exam_json['num_completion'])

    # 判断题
    data_tf = _load_problem(
        path=joindir(path, 'TrueOrFalse.csv'),
        converters={'id': int, 'description': str, 'answer': str, 'tag': str},
        tag=exam_json['tag_trueorfalse'], num=exam_json['num_trueorfalse'])

    # 程序改错题
    data_pc = _load_problem(
        path=joindir(path, 'ProgramCorrection.csv'),
        converters={'id': int, 'description': str, 'template': str, 'test_case_id': str, 'tag': str},
        tag=exam_json['tag_programcorrection'], num=exam_json['num_programcorrection'])

    # 程序阅读题
    data_pr = _load_problem(
        path=joindir(path, 'ProgramReading.csv'),
        converters={'id': int, 'description': str, 'answer': str, 'tag': str},
        tag=exam_json['tag_programreading'], num=exam_json['num_programreading'])

    # 程序设计题
    data_pd = _load_problem(
        path=joindir(path, 'ProgramDesign.csv'),
        converters={'id': int, 'description': str, 'test_case_id': str, 'tag': str},
        tag=exam_json['tag_programdesign'], num=exam_json['num_programdesign'])

    ans = {
        'choice': data_ch,
        'completion': data_cp,
        'true_or_false': data_tf,
        'program_correction': data_pc,
        'program_reading': data_pr,
        'program_design': data_pd,
    }
    
    return ans

@login_required
def exam_legency(request):
    
    if request.method == 'GET':
        # >>>> 生成并且载入试题 <<<<
        
        data = {
            'choice': [],
            'completion': [],
            'true_or_false': [],
            'program_correction': [],
            'program_reading': [],
            'program_design': [],
        }

        # 该用户是否有此次考试的权限
        permission_flag = False
        if 'id' in request.GET:
            exam_id = request.GET['id']

            # get user's classes id
            if request.user.is_staff:
                # represent match any classes
                user_classes = None
            else:
                user_classes = request.user.myuser.classes

            user_name = request.user.username
            path = 'data/exams'
            filename = joindir(path, '{}.json'.format(exam_id))
            if isfile(filename):
                with open(filename, 'r') as f:
                    exam_json = json.load(f)
                if (user_classes is not None) and (exam_json['classes'] != user_classes):
                    messages.error(request, '您不能参加此次考试')
                else:
                    exam_ress = ExamResult.objects.filter(username=user_name, examname=exam_id)
                    if (len(exam_ress) > 0) and (user_classes is not None) and (exam_ress[0].is_submitted == 1):
                        messages.success(request, '您已经完成此次考试')
                        data = exam_ress[0].data.copy()
                        data.update({'score': exam_ress[0].score})
                        return render(request, 'exam_submit.html', data)
                    else:
                        permission_flag = True
            else:
                messages.error(request, '考试{}不存在'.format(exam_id))
        else:
            messages.error(request, '请在考试列表中选择您要参加的考试')

        if permission_flag:
            if len(exam_ress) > 0:
                # 如果非首次登陆，载入该用户此次考试的题目
                data = exam_ress[0].data
            else:
                # 如果首次登陆，生成考试题目，并存下该用户此次考试的题目
                problems = load_problem_base(exam_json)

                data = problems_to_data(problems, exam_json)

                exam_res = ExamResult(username=user_name, examname=exam_id, 
                    data=data, is_submitted=0, examjson=exam_json)
                exam_res.save()

        return render(request, 'exam.html', process_for_render(data))
    
    elif request.method == 'POST':
        
        # >>>> 保存试题或者提交判分 <<<<
        # 样例 request.post = <QueryDict: {'2_A': ['on'], 'save': ['']}>
        
        exam_id = request.GET['id']
        user_name = request.user.username

        if 'save' in request.POST:
            # 保存结果
            exam_res = ExamResult.objects.get(username=user_name, examname=exam_id)
            exam_res.data = post_to_answers(exam_res.data, request.POST)
            exam_res.save()

            messages.success(request, '保存成功')

            return render(request, 'exam.html', process_for_render(exam_res.data))

        elif 'submit' in request.POST:
            # 提交并且判分
            exam_res = ExamResult.objects.get(username=user_name, examname=exam_id)
            exam_res.data = post_to_answers(exam_res.data, request.POST, exam_res.examjson)
            exam_res.data = score_answers(exam_res.data)
            exam_res.score = generate_total_score(exam_res.data)
            exam_res.is_submitted = 1
            exam_res.save()

            messages.success(request, '提交成功')

            data = exam_res.data.copy()
            data.update({'score': exam_res.score})

            return render(request, 'exam_submit.html', process_for_render(data))

@login_required
def examlist_legency(request):
    """
    显示考试列表，显示考试班级和用户班级相同的考试，并且装到dict里面传递给render
    """
    path = 'data/exams'
    # get user's classes id
    if request.user.is_staff:
        # represent match any classes
        user_classes = None
    else:
        user_classes = request.user.myuser.classes
    # list all the exams 
    exam_list = listdir(path)
    exam_list = [item for item in exam_list if re.match('.*\.json', item)]
    
    exam_jsons = []
    for exam in exam_list:
        with open(joindir(path, exam), 'r') as f:
            exam_json = json.load(f)
            exam_json['id'] = exam.replace('.json', '')
            if  user_classes is None or exam_json['classes'] == user_classes:
                exam_jsons.append(exam_json)
                
    exam_list = [{'name': j['name'], 'id': j['id']} for j in exam_jsons]
    
    return render(request, 'examlist.html', {'exam_list': exam_list})
