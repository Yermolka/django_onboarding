from django.http import HttpResponse, HttpRequest, Http404
from django.template import loader
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Survey, OnboardingUser, Question, Answer, User

from typing import List

# При создании юзера вручную автоматически не создается OnboardingUser
# Если за текущим юзером не закреплен OnboardingUser, то нужно его создать
def check_for_onboarding_user(user: User):
    if user.id and OnboardingUser.objects.filter(user__id=user.id).first():
        return
    
    u = OnboardingUser(user=user)
    u.save()

# На входной странице либо регистрация/логин, 
# либо редирект на список опросов
def index(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect('login')
    
    check_for_onboarding_user(request.user)

    return redirect('surveys')

@login_required
def surveys(request: HttpRequest):
    template = loader.get_template('survey/surveys.html')
    context = {
        'surveys': Survey.objects.all()[:]
    }
    return HttpResponse(template.render(context, request))

@login_required
def survey(request: HttpRequest, survey_id: int):
    questions = Question.objects.filter(survey__id=survey_id).all()[:]
    if not questions:
        raise Http404()
    
    return redirect('survey_question', survey_id=survey_id, question_id=questions[0].id)

# Если выполнены условия вопроса - показать
# Иначе находим ближайший доступный
@login_required
def survey_question(request: HttpRequest, survey_id: int, question_id: int):
    check_for_onboarding_user(request.user)
    question = get_object_or_404(Question, id=question_id)
    user = OnboardingUser.objects.get(user__id=request.user.id)
    user_old_answers = user.answers.filter(survey__id=survey_id).all()[:]

    errors = []
    if request.method == 'POST' and 'forward' in request.POST:
        request_items = request.POST.items()
        choices = []
        for key, value in request_items:
            if not key.startswith('choice'):
                continue
            choices.append(int(value))
        if not choices:
            errors.append('Необходимо выбрать ответ.')
        else:
            return survey_question_post(request, survey_id, question_id, user, user_old_answers, choices)
    elif request.method == 'POST' and 'back' in request.POST:
        return redirect(request.session.get('prev_url', 'surveys'), *request.session.get('prev_params', []))

    context = {
        'survey_id': survey_id,
        'survey_name': question.survey.name,
        'question': question,
        'answers': question.possible_answers.all()[:],
        'errors': errors,
        'user_answers': [ans.id for ans in user_old_answers]
    }

    # For CFRS
    return render(request, 'survey/question.html', context)

@login_required
def survey_question_post(request: HttpRequest, survey_id: int, question_id: int, user: OnboardingUser, user_old_answers, choices: List[int]):
            
    # Для работы кнопки "назад"
    request.session['prev_url'] = 'survey_question'
    request.session['prev_params'] = [survey_id, question_id]

    # Обновляем ответы пользователя в БД
    for ans in user_old_answers:
        user.answers.remove(ans.id)
    for c in choices:
        c = int(c)
        user.answers.add(c)
    
    user.save()
    

    # Переходим на следующий доступный вопрос
    all_questions = Question.objects \
                            .filter(survey__id=survey_id) \
                            .filter(id__gt=question_id) \
                            .all()[:]

    user_answers = user.answers.all()[:]

    for q in all_questions:
        required_answers = q.required_answers.all()[:]
    
        if q.constraint == Question.PreviousConstraint.NONE:
            return redirect('survey_question', survey_id=survey_id, question_id=q.id)
        
        if q.constraint == Question.PreviousConstraint.ANY:
            for answer in required_answers:
                if answer in user_answers:
                    return redirect('survey_question', survey_id=survey_id, question_id=q.id)
                
        if q.constraint == Question.PreviousConstraint.ALL:
            for answer in required_answers:
                if answer not in user_answers:
                    break
            else:
                return redirect('survey_question', survey_id=survey_id, question_id=q.id)
    
    request.session.pop('prev_url')
    request.session.pop('prev_params')
    return redirect('surveys')
                
def register(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'registration/register.html')
    
    username = request.POST.get('username')
    password = request.POST.get('password')

    if User.objects.filter(username=username).first():
        return render(request, 'registration/register.html', {'errors': ['Пользователь с таким именем уже существует.']})
    new_user = User(username=username)
    new_user.set_password(password)
    new_user.save()

    new_onboarding_user = OnboardingUser(user=new_user)
    new_onboarding_user.save()

    request.user = new_user
    return redirect('surveys')