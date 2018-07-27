from django.contrib import admin
from backend.models import MyUser, ExamResult, Exam, Problem

admin.site.register(MyUser)
admin.site.register(ExamResult)
admin.site.register(Exam)
admin.site.register(Problem)