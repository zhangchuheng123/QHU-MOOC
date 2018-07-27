from django.db import models
# from django.contrib.postgres.fields import JSONField
from django_mysql.models import JSONField
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.models import User

class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    STUDENT = 1
    TEACHER = 2
    usertype = models.SmallIntegerField(choices=(
        (STUDENT, '学生'),
        (TEACHER, '教师'),
    ), default=STUDENT, verbose_name='用户类型')
    classes = models.CharField(max_length=200, verbose_name='班级')
    
    def __str__(self):
        return '【{:<20}】 class:{:<10} usertype:{:<5}'\
            .format(self.user.username, self.classes, '学生' if self.usertype == 1 else '教师')
    
class Exam(models.Model):
    eid = models.CharField(max_length=200, verbose_name='考试唯一识别标志符')
    name = models.CharField(max_length=200, verbose_name='考试名称')
    classes = models.CharField(max_length=200, verbose_name='考试对应的班级')
    
    num_choice = models.PositiveSmallIntegerField(verbose_name='选择题数目')
    point_choice = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='每题选择题分数')
    tag_choice = models.CharField(max_length=200, verbose_name='选择题题库标签')
    
    num_completion = models.PositiveSmallIntegerField(verbose_name='填空题数目')
    point_completion = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='每题填空题分数')
    tag_completion = models.CharField(max_length=200, verbose_name='填空题题库标签')
    
    num_trueorfalse = models.PositiveSmallIntegerField(verbose_name='判断题数目')
    point_trueorfalse = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='每题判断题分数')
    tag_trueorfalse = models.CharField(max_length=200, verbose_name='判断题题库标签')
    
    num_programcorrection = models.PositiveSmallIntegerField(verbose_name='程序改错题数目')
    point_programcorrection = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='每题程序改错题分数')
    tag_programcorrection = models.CharField(max_length=200, verbose_name='程序改错题题库标签')
                                  
    num_programreading = models.PositiveSmallIntegerField(verbose_name='程序阅读题数目')
    point_programreading = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='每题程序阅读题分数')
    tag_programreading = models.CharField(max_length=200, verbose_name='程序阅读题题库标签')
    
    num_programdesign = models.PositiveSmallIntegerField(verbose_name='程序设计题数目')
    point_programdesign = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='每题程序设计题分数')
    tag_programdesign = models.CharField(max_length=200, verbose_name='程序设计题题库标签')
    
    def __str__(self):
        return '【{}】 eid: {} class:{}'.format(self.name, self.eid, self.classes)
    
class Problem(models.Model):

    CHOICE = 0
    COMPLETION = 1
    TRUEORFALSE = 2
    PROGRAMCORRECTION = 3
    PROGRAMREADING = 4
    PROGRAMDESIGN = 5

    problem_type = models.SmallIntegerField(choices=(
        (CHOICE, '选择题'),
        (COMPLETION, '填空题'),
        (TRUEORFALSE, '判断题'),
        (PROGRAMCORRECTION, '程序改错题'),
        (PROGRAMREADING, '程序阅读题'),
        (PROGRAMDESIGN, '程序设计题'),
    ), verbose_name='题库类型')

    pid = models.PositiveIntegerField(verbose_name='题目编号')
    description = models.TextField(verbose_name='题干描述')
    template = models.TextField(verbose_name='程序模板（仅程序改错题）')
    choice_A = models.CharField(max_length=400, verbose_name='A选项（仅选择题）')
    choice_B = models.CharField(max_length=400, verbose_name='B选项（仅选择题）')
    choice_C = models.CharField(max_length=400, verbose_name='C选项（仅选择题）')
    choice_D = models.CharField(max_length=400, verbose_name='D选项（仅选择题）')
    answer = models.CharField(max_length=200, verbose_name='标准答案（除程序改错和设计）')
    test_case_id = models.CharField(max_length=200, verbose_name='测试点id（仅程序改错和设计）')
    tag = models.CharField(max_length=200, verbose_name='该题标签')
    
    def __str__(self):
        return '【{}】 pid: {} tag:{}'.format(self.to_name(self.problem_type), self.pid, self.tag)
    
    @staticmethod
    def to_name(x):
        if x == 0:
            return '选择题'
        elif x == 1:
            return '填空题'
        elif x == 2:
            return '判断题'
        elif x == 3:
            return '程序改错题'
        elif x == 4:
            return '程序阅读题'
        elif x == 5:
            return '程序设计题'
    
class ExamResult(models.Model):
    username = models.CharField(max_length=200, verbose_name='用户名')
    examname = models.CharField(max_length=200, verbose_name='考试名称')
    score = models.DecimalField(decimal_places=2, max_digits=5, default=0.0, verbose_name='总分')
    exam = models.OneToOneField(Exam, on_delete=models.CASCADE, verbose_name='所属考试')
    data = JSONField(blank=True, null=True, verbose_name='辅助数据（考试题目和用户答案）')
    UNSUBMITTED = 0
    SUBMITTED = 1
    is_submitted = models.SmallIntegerField(choices=(
        (UNSUBMITTED, '未提交'),
        (SUBMITTED, '已提交'),
    ), default=UNSUBMITTED, verbose_name='是否提交')
    
    def __str__(self):
        return '【{} - {}】 score: {}'.format(self.username, self.examname, self.score if self.is_submitted == 1 else '未提交')
    