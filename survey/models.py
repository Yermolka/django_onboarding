from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as gtl

class Survey(models.Model):
    name = models.CharField(
        verbose_name='Название', 
        max_length=100)

    def __str__(self):
        return f'{self.id}: {self.name}'

class Answer(models.Model):
    text = models.CharField(
        verbose_name='Ответ', 
        max_length=100)
    
    survey = models.ForeignKey(
        Survey, 
        verbose_name='Опрос',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.survey.name}, {self.id}: {self.text}'

class Question(models.Model):
    class AnswerConstraint(models.enums.TextChoices):
        SINGLE = 'SINGLE', gtl('Один из списка')
        MULTIPLE = 'MULTIPLE', gtl('Несколько из списка')

    # Поля для проверки показывать или нет
    class PreviousConstraint(models.enums.TextChoices):
        ANY = 'ANY', gtl('Любой из ответов')
        ALL = 'ALL', gtl('Все ответы')
        NONE = 'NONE', gtl('Нет')

    survey = models.ForeignKey(
        Survey, 
        verbose_name='Опрос',
        on_delete=models.CASCADE)

    text = models.CharField(
        verbose_name='Текст вопроса:', 
        max_length=100)

    constraint = models.CharField(
        verbose_name='Условие',
        max_length=4, 
        choices=PreviousConstraint.choices, 
        default=PreviousConstraint.NONE
        )

    required_answers = models.ManyToManyField(
        Answer,
        blank=True,
        verbose_name='Необходимые предыдущие ответы',
        related_name='required_answers')

    multiple_answers = models.CharField(
        verbose_name='Выбор ответов',
        max_length=8, 
        choices=AnswerConstraint.choices, 
        default=AnswerConstraint.SINGLE
        )
    
    possible_answers = models.ManyToManyField(
        Answer,
        verbose_name='Варианты ответа',
        related_name='possible_answers'
    )

    def __str__(self):
        return f'{self.id}: {self.text}'
    
class OnboardingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    answers = models.ManyToManyField(
        Answer,
        blank=True,
        verbose_name='Ответы пользователя'
    )

    def __str__(self):
        return f'{self.id}: {self.user.username}'