from django.contrib import admin
from backend.models import MyUser, ExamResult, Exam, Problem

class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'usertype', 'classes')

class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('username', 'examname', 'score', 'is_submitted', 'program_design_score')
    readonly_fields = ('source_code',)
    fieldsets = (
        (None, {
            'fields': ('username', 'examname', 'score', 'exam', 'is_submitted', 'source_code')
        }),
        ('辅助数据', {
            'classes': ('collapse',),
            'fields': ('data',),
        }),
    )
    
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'eid', 'classes', 'num_choice', 'num_completion', 'num_trueorfalse', 
        'num_programcorrection', 'num_programreading', 'num_programdesign', 'total_score',
    )
    readonly_fields = ('notice_text',)
    fieldsets = (
        ('试卷基本信息', {
            'fields': ('eid', 'name', 'classes', 'notice_text'),
        }),
        ('选择题', {
            'fields': ('num_choice', 'point_choice', 'tag_choice'),
        }),
        ('填空题', {
            'fields': ('num_completion', 'point_completion', 'tag_completion'),
        }),
        ('判断题', {
            'fields': ('num_trueorfalse', 'point_trueorfalse', 'tag_trueorfalse'),
        }),
        ('程序改错题', {
            'fields': ('num_programcorrection', 'point_programcorrection', 'tag_programcorrection'),
        }),
        ('程序阅读题', {
            'fields': ('num_programreading', 'point_programreading', 'tag_programreading'),
        }),
        ('程序设计题', {
            'fields': ('num_programdesign', 'point_programdesign', 'tag_programdesign'),
        }),
    )
    
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('problem_type', 'pid', 'tag')
    fieldsets = (
        (None, {
            'fields': (('problem_type', 'pid'), 'description', 'tag', 'answer')
        }),
        ('选择题选项', {
            'classes': ('collapse',),
            'fields': ('choice_A', 'choice_B', 'choice_C', 'choice_D'),
        }),
        ('程序题设计和改错题', {
            'classes': ('collapse',),
            'fields': ('template', 'test_case_id'),
        }),
    )

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(ExamResult, ExamResultAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Problem, ProblemAdmin)