from django.contrib import admin
from .models import (Survey, 
                     Question, 
                     Answer,
                     OnboardingUser)

# class AnswerInline(admin.TabularInline):
#     model = Answer

class QuestionInline(admin.TabularInline):
    model = Question

class SurveyAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

# class QuestionAdmin(admin.ModelAdmin):
#     inlines = [AnswerInline]


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(OnboardingUser)