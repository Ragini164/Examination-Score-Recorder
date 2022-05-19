# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import math
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models import Sum
import requests
from .models import course, user, topic, subtopic, question_type, level, exam_detail, question_bank,  option, answer, registration, result, MatchTheColumns
from . import exponential_tree


def faculty_register_evaluate(request):
    Exp=exponential_tree.ExponentialTree()
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        # if(request.method == "GET"):
        #     ans = registration.objects.get(pk = int(request.POST["registration_id"])).view_answers
        #     ans = 1 - int(ans)
        #     registration.objects.filter(pk = int(request.POST["registration_id"])).update(view_answers = ans)
        #     return HttpResponse(ans)
        query = []
        prev=None
        for i in result.objects.all():
            
            if(i.registration_id==prev):
                continue
            subquery = dict()
            subquery["first_name"] = i.registration_id.user_id.first_name
            subquery["last_name"] = i.registration_id.user_id.last_name
            subquery["attempt_no"] = i.registration_id.attempt_no
            subquery["course"] = i.registration_id.exam_id.course_id.course_name
            subquery["year"] = i.registration_id.exam_id.year
            subquery["exam_id"] = exam_detail.objects.get(id=i.registration_id.exam_id.id)
            subquery["id"] = i.id
            if(result.objects.filter(id = i.id).count() == result.objects.filter(registration_id = i.registration_id, verify = 1).count()):
                subquery["verify"] = 1
            else:
                subquery["verify"] = 0
            subquery["view_answers"] = i.registration_id.view_answers
            subquery["score"] = result.objects.filter(registration_id = i.registration_id).aggregate(Sum('score'))
            if(subquery["score"]["score__sum"] == None):
                subquery["score"] = 0
            else:
                subquery["score"] = int(subquery["score"]["score__sum"])
            print(subquery)
            query.append(subquery)
            Exp.insert(subquery)
            prev=i.registration_id
        query=Exp.inorderTraversal(Exp.root) #storing the result of inorder traversal
        
        return render(request ,'online_exam/faculty_register_evaluate.html', {"registrations": query})
    else:
        return redirect("../login")

def faculty_manual_evaluate(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method == "POST":
            if request.POST.get('result_id', False) != False and request.POST.get('check', False) != False and request.POST.get('score', False) != False: 
                if(int(request.POST['check']) == 1):
                    result.objects.filter(pk = int(request.POST['result_id'])).update(score = int(request.POST['score']), verify = 1)
                elif(int(request.POST['check']) == 0):
                    result.objects.filter(pk = int(request.POST['result_id'])).update(score = 0, verify = 1)
                data = dict()
                z = 1
                for i in result.objects.filter(registration_id = registration.objects.get(pk = request.POST["user_exam_attempt_id"])).all():
                    subdata = dict()
                    subdata['question_id'] = i.question_id.id
                    subdata['question'] = i.question_id.question
                    subdata['question_type'] = i.question_id.question_type.q_type
                    if(i.question_id.question_type.id == 1 or i.question_id.question_type.id == 2):
                        opt_dict = dict()
                        for k in option.objects.filter(question_id = i.question_id.id):
                            opt_dict[k.option_no] = k.option_value
                        subdata['options'] = opt_dict
                    else:
                        subdata['options'] = ""
                    subdata["result_id"] = i.id
                    if(subdata['question_type']  == "Multiple Choice Single Answer" or subdata['question_type'] == "Multiple Choice Multiple Answer"):
                        answers = ""
                        for j in answer.objects.filter(question_id = i.question_id).all():
                            answers += (option.objects.get(question_id = i.question_id, option_no=j.answer).option_value + "; ")
                        subdata['answer'] = answers
                    elif(subdata['question_type'] == "Match the Column"):
                        subdata['answer'] = ""
                        for j in MatchTheColumns.objects.filter(question_id = i.question_id).all():
                            subdata['answer'] += j.question + " - " + j.answer + "; "
                    else: 
                        subdata['answer'] = answer.objects.get(question_id = i.question_id).answer
                    subdata['level'] = i.question_id.level_id.level_name
                    subdata['score'] = i.question_id.score
                    subdata['gained_score'] = i.score
                    subdata['your_answers'] = i.answer
                    subdata['verify'] = i.verify
                    data[z] = subdata
                    z += 1
                data = json.dumps(data)
                return HttpResponse(data)
            data = dict()
            z = 1
            for i in result.objects.filter(registration_id = registration.objects.get(pk = int(request.POST['registration_id']))).all():
                subdata = dict()
                subdata['question_id'] = i.question_id.id
                subdata['question'] = i.question_id.question
                subdata['question_type'] = i.question_id.question_type.q_type
                if(i.question_id.question_type.id == 1 or i.question_id.question_type.id == 2):
                    opt_dict = dict()
                    for k in option.objects.filter(question_id = i.question_id.id):
                        opt_dict[k.option_no] = k.option_value
                    subdata['options'] = opt_dict
                else:
                    subdata['options'] = ""
                subdata["result_id"] = i.id
                if(subdata['question_type']  == "Multiple Choice Single Answer" or subdata['question_type'] == "Multiple Choice Multiple Answer"):
                    answers = ""
                    for j in answer.objects.filter(question_id = i.question_id).all():
                        answers += (option.objects.get(question_id = i.question_id, option_no=j.answer).option_value + "; ")
                    subdata['answer'] = answers
                elif(subdata['question_type'] == "Match the Column"):
                    subdata['answer'] = ""
                    for j in MatchTheColumns.objects.filter(question_id = i.question_id).all():
                        subdata['answer'] += j.question + " - " + j.answer + "; "
                else: 
                    subdata['answer'] = answer.objects.get(question_id = i.question_id).answer
                subdata['level'] = i.question_id.level_id.level_name
                subdata['score'] = i.question_id.score
                subdata['gained_score'] = i.score
                subdata['your_answers'] = i.answer
                subdata['verify'] = i.verify
                data[z] = subdata
                z += 1
            data = json.dumps(data)
            return render(request ,'online_exam/faculty_manual_evaluate.html', {"data":data, "exam_id":1, "registration_id":1})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_profile(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.method=='POST'):
            if(request.POST.get('password', False) != False):
                user.objects.filter(pk=request.session['id']).update(password=make_password(request.POST['password']))
                message = "Password Updated Successfully!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            if(user.objects.filter(email = request.POST['email']).count() == 1 and user.objects.filter(email = request.POST['email'], id = request.session['id']).count() == 1):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            elif(user.objects.filter(email = request.POST['email']).count() == 0):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            else:
                wrong_message = "Sorry email id already exists!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "wrong_message":wrong_message})
        temp=user.objects.get(pk=int(request.session['id']))
        currentUser = user()
        currentUser.first_name = temp.first_name
        currentUser.last_name = temp.last_name
        currentUser.phone = temp.phone
        currentUser.email = temp.email
        currentUser.account_type = temp.account_type
        currentUser.id = temp.id
        return render(request, "online_exam/faculty_profile.html", {"currentUser" : currentUser})
    else:
        return redirect("../login")
# Create your views here.
def student_dashboard(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        perform = []
        for i in registration.objects.filter(user_id = user.objects.get(id = request.session['id']), answered = 1).all():
            perf = dict()
            perf["exam_name"] = i.exam_id.exam_name
            gained_score = result.objects.filter(registration_id = i.id).aggregate(Sum('score'))
            if(gained_score['score__sum'] == None):
                gained_score = 0
            else:
                gained_score = int(gained_score['score__sum'])
            total_score = 0
            for j in result.objects.filter(registration_id = i.id).all():
                total_score += j.question_id.score
            if(total_score == 0):
                perf["percentage"] = 0
            else:
                perf["percentage"] = gained_score/total_score * 100
            perform.append(perf)
        now = datetime.datetime.now()
        curr = str(now.year) + "-" + str(now.month) + "-01"
        curr_year = int(now.year)
        curr_month = int(now.month)
        dataArray = []
        for i in range(0, 6):
            if(curr_month-i <= 0):
                curr_year -= 1
                curr_month += 12
            curr_array = dict()
            curr_array["year"] = curr_year
            curr_array["month"] = curr_month - i -1
            if(curr_month - i != 12):
                curr_array["count"] = registration.objects.filter(answered = 1, registered_time__range = (datetime.date(curr_year, curr_month-i, 1), datetime.date(curr_year, curr_month-i + 1, 1))).count()
            else:
                curr_array["count"] = registration.objects.filter(answered = 1, registered_time__range = (datetime.date(curr_year, 12, 1), datetime.date(curr_year+1, 1, 1))).count()
            dataArray.append(curr_array)
        pass_p = 0
        count = 0
        for i in registration.objects.filter(answered=1, view_answers = 1, user_id = user.objects.get(pk = request.session["id"])).all():
            gained_score = result.objects.filter(registration_id = i).aggregate(Sum('score'))
            if(gained_score['score__sum'] == None):
                gained_score = 0
            else:
                gained_score = int(gained_score['score__sum'])
            total_score = 0
            for j in result.objects.filter(registration_id = i).all():
                total_score += j.question_id.score
            if(gained_score >= i.exam_id.pass_percentage*total_score/100):
                pass_p += 1
            count += 1
        if(count == 0):
            pass_percentage = 0
        else:
            pass_percentage = pass_p*100/count
        return render(request, 'online_exam/student_dashboard.html', {"number_of_exams":exam_detail.objects.count(), "no_of_users":user.objects.count(), "pass_percentage":pass_percentage, "dataArray":dataArray, "performance":perform})
    else:
        return redirect("../login")

def student_exams(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        Final = dict()
        if(request.method == "POST" and request.POST.get('exam_id', False) != False):
            temp = registration()
            temp.user_id = user.objects.get(id = request.session['id'])
            temp.exam_id = exam_detail.objects.get(id = int(request.POST['exam_id']))
            temp.attempt_no = 0
            temp.save()
            Final["message"] = "Applied for registration successfully!!"
        exams = []
        for i in exam_detail.objects.filter(status="1").all():
            tmpdct = dict()
            tmpdct["id"] = i.id
            tmpdct["exam_name"] = i.exam_name
            tmpdct["description"] = i.description
            tmpdct["course_name"] = i.course_id.course_name
            tmpdct["year"] = i.year
            user_id = user.objects.get(id = request.session['id'])
            exam_id = i
            tmpdct["attempts_left"] = int(i.attempts_allowed) - registration.objects.filter(user_id = user_id, exam_id = exam_id).count()
            exams.append(tmpdct)
        Final["exams"] = exams
        return render(request, 'online_exam/student_exams.html', Final)
    else:
        return redirect("../login")

def student_attempt_exam(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        print(request.POST['exam_id'])
        questions = question_bank.objects.filter(exam_id = exam_detail.objects.get(id = int(request.POST['exam_id']))).all()
        K = dict()
        registration_id = request.POST['registration_id']
        exam_id = ""
        j = 0
        for i in questions:
            L = dict()
            L['question_id'] = i.id
            L['question'] = i.question
            L['question_type'] = i.question_type.q_type
            if(i.question_type.id == 1 or i.question_type.id == 2):
                opt_dict = dict()
                for k in option.objects.filter(question_id = i.id):
                    opt_dict[k.option_no] = k.option_value
                L['options'] = opt_dict
            else:
                L['options'] = ""
            #L['answer'] = dict(answer.objects.filter(question_id = i.id).values("answer"))
            if(i.question_type.id == 5):
                m = 1
                L['mtcQuestions'] = dict()
                L['mtcAnswers'] = dict()
                for l in MatchTheColumns.objects.filter(question_id = i).all():
                    L['mtcQuestions'][m] = l.question    
                    m += 1
                m = 1
                for l in MatchTheColumns.objects.filter(question_id = i).order_by('?').all():
                    L['mtcAnswers'][m] = l.answer    
                    m += 1
            L['level'] = i.level_id.level_name
            L['subtopic'] = i.subtopic_id.subtopic_name
            L['topic'] = i.subtopic_id.topic_id.topic_name
            L['score'] = i.score
            L['exam'] = i.exam_id.exam_name
            exam_id = i.exam_id.id
            L['course'] = i.exam_id.course_id.course_name
            j += 1
            K[j] = L
            final = json.dumps(K)
            a = datetime.datetime.now()
            b = datetime.datetime(i.exam_id.end_time.year,i.exam_id.end_time.month,i.exam_id.end_time.day,i.exam_id.end_time.hour,i.exam_id.end_time.minute,i.exam_id.end_time.second)
            seconds = math.floor((b-a).total_seconds())
        return render(request, 'online_exam/student_attempt_exam.html', {"myArray":final, "sizeMyArray":j, "exam_id":exam_id, "registration_id":registration_id, "seconds": seconds})
    else:
        return redirect("../login")
def student_approved_exams(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        Final = []
        for i in registration.objects.filter(user_id = user.objects.get(pk = int(request.session['id']))): 
            exams = dict()
            print(i.exam_id.id)
            exams["registration_id"] = i.id
            exams["exam_id"] = i.exam_id.id
            exams["exam_name"] = i.exam_id.exam_name
            exams["start_time"] = i.exam_id.start_time
            exams["end_time"] = i.exam_id.end_time
            exams["course_name"] = i.exam_id.course_id.course_name
            exams["description"] = i.exam_id.description
            exams["attempt_no"] = i.attempt_no
            exams["no_of_questions"] = i.exam_id.no_of_questions
            exams["pass_percentage"] = i.exam_id.pass_percentage
            start_time = i.exam_id.start_time
            end_time = i.exam_id.end_time
            if(start_time <= timezone.now() and end_time >= timezone.now() and i.answered == 0 and i.registered == 1):
                exams["attemptable"] = 1
            else:
                exams["attemptable"] = 0
            Final.append(exams)
        return render(request, 'online_exam/student_approved_exams.html', {"exams":Final, "current_time":datetime.datetime.now()}) 
    else:
        return redirect("../login")

def student_verify(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        attempted = json.loads(request.POST.get("answer", False))
        registration.objects.filter(id = request.POST["registration_id"]).update(answered = 1)
        marks = 0
        for i in attempted.keys():
            attempted_answer = dict(attempted[i])
            print(attempted_answer['answers'])
            #print(attempted_answer['question_id'])
            ans = dict()
            ques = question_bank.objects.get(pk = attempted_answer['question_id'])
            ques_type = ques.question_type.q_type
            if(ques_type == "Multiple Choice Single Answer" or ques_type == "Multiple Choice Multiple Answer"):
                for j in answer.objects.filter(question_id = ques).all():
                    opt = option.objects.get(question_id = ques, option_no=j.answer)
                    ans[opt.option_no] = opt.option_value
                temp = result()
                temp.registration_id = registration.objects.get(pk = int(request.POST["registration_id"]))
                temp.question_id = ques
                temp.answer = ""
                for j in attempted_answer["answers"].keys():
                    temp.answer += attempted_answer["answers"][j] + "; "
                if(json.dumps(ans) == json.dumps(attempted_answer['answers'])):
                    temp.score = int(attempted_answer['score'])
                else:
                    temp.score = 0
                marks += temp.score
                temp.verify = 1
                temp.save()
            elif(ques_type == "Match the Column"):
                for j in MatchTheColumns.objects.filter(question_id = ques).all():
                    ans[j.question] = j.answer
                temp = result()
                temp.question_id = ques
                temp.registration_id = registration.objects.get(pk = int(request.POST["registration_id"]))
                temp.answer = ""
                for j in attempted_answer["answers"].keys():
                    temp.answer += j + " - " + attempted_answer["answers"][j] + "; "
                if(json.dumps(ans) == json.dumps(attempted_answer['answers'])):
                    temp.score = int(attempted_answer['score'])
                else:
                    temp.score = 0
                marks += temp.score
                temp.verify = 1
                temp.save()
            else:
                temp = result()
                temp.registration_id = registration.objects.get(pk = int(request.POST["registration_id"]))
                temp.question_id = ques
                temp.answer = dict(attempted_answer['answers'])
                temp.answer = temp.answer['1']
                temp.score = 0
                temp.verify = 0
                temp.save()                 
        return HttpResponse(marks)
    else:
        return redirect("../login")

def student_progress(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        query = []
        for i in registration.objects.filter(user_id = user.objects.get(pk = request.session['id']), answered = 1, view_answers = 1).all():
            subquery = dict()
            subquery["exam_name"] = i.exam_id.exam_name
            subquery["attempt_no"] = i.attempt_no
            subquery["course"] = i.exam_id.course_id.course_name
            subquery["year"] = i.exam_id.year
            subquery["id"] = i.id
            if(result.objects.filter(registration_id = i).count() == result.objects.filter(registration_id = i, verify = 1).count()):
                subquery["verify"] = 1
            else:
                subquery["verify"] = 0
            subquery["view_answers"] = i.view_answers
            subquery["score"] = result.objects.filter(registration_id = i).aggregate(Sum('score'))
            if(subquery["score"] == None):
                subquery["score"] = 0
            else:
                subquery["score"] = int(subquery["score"]["score__sum"])
            query.append(subquery)
        return render(request, 'online_exam/student_progress.html', {"registrations":query})
    else:
        return redirect("../login")

def student_answer_key(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        data = []
        for i in result.objects.filter(registration_id = registration.objects.get(pk = request.POST['registration_id'])).all():
            subdata = dict()
            subdata['question_id'] = i.question_id.id
            subdata['question'] = i.question_id.question
            subdata['question_type'] = i.question_id.question_type.q_type
            if(i.question_id.question_type.id == 1 or i.question_id.question_type.id == 2):
                options = ""
                for j in option.objects.filter(question_id = i.question_id.id).all():
                    options += (j.option_value + "; ")
                subdata['options'] = options
            else:
                subdata['options'] = "-"
            subdata["result_id"] = i.id
            if(subdata['question_type']  == "Multiple Choice Single Answer" or subdata['question_type'] == "Multiple Choice Multiple Answer"):
                answers = ""
                for j in answer.objects.filter(question_id = i.question_id).all():
                    answers += (option.objects.get(question_id = i.question_id, option_no=j.answer).option_value + "; ")
                subdata['answer'] = answers
            elif(subdata['question_type'] == "Match the Column"):
                subdata['answer'] = ""
                for j in MatchTheColumns.objects.filter(question_id = i.question_id).all():
                    subdata['answer'] += j.question + " - " + j.answer + "; "
            else: 
                subdata['answer'] = answer.objects.get(question_id = i.question_id).answer
            subdata['level'] = i.question_id.level_id.level_name
            subdata['score'] = i.question_id.score
            subdata['gained_score'] = i.score
            subdata['your_answers'] = i.answer
            subdata['verify'] = i.verify
            data.append(subdata)
        return render(request, 'online_exam/student_answer_key.html', {"data":data})
    else:
        return redirect("../login")

def student_profile(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        if(request.method=='POST'):
            if(request.POST.get('password', False) != False):
                user.objects.filter(pk=request.session['id']).update(password=make_password(request.POST['password']))
                message = "Password Updated Successfully!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            if(user.objects.filter(email = request.POST['email']).count() == 1 and user.objects.filter(email = request.POST['email'], id = request.session['id']).count() == 1):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            elif(user.objects.filter(email = request.POST['email']).count() == 0):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            else:
                wrong_message = "Sorry email id already exists!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "wrong_message":wrong_message})
        temp=user.objects.get(pk=int(request.session['id']))
        currentUser = user()
        currentUser.first_name = temp.first_name
        currentUser.last_name = temp.last_name
        currentUser.phone = temp.phone
        currentUser.email = temp.email
        currentUser.account_type = temp.account_type
        currentUser.id = temp.id
        return render(request, 'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id'])})
    else:
        return redirect("../login")

def login(request):
    if(request.session.get('id', False) == False):
        if(request.method == "POST" and request.POST.get('email', False) != False and request.POST.get('password', False) != False):
            if(user.objects.filter(email = request.POST['email']).exists()):
                login_user = user.objects.get(email = request.POST['email'])
                if (check_password(request.POST.get('password', False),login_user.password) == True):
                    request.session['id'] = login_user.id
                    request.session['first_name'] = login_user.first_name
                    request.session['last_name'] = login_user.last_name
                    request.session['email'] = login_user.email
                    request.session['phone'] = login_user.phone
                    request.session['account_type'] = login_user.account_type
                    return redirect('../login')
                else:
                    return render(request, 'online_exam/Login.html', {"message":"Invalid Credentials!!"})
            else:
                return render(request, 'online_exam/Login.html', {"message":"Invalid Credentials!!"})
        return render(request, 'online_exam/Login.html')
    elif(request.session.get('account_type', False) == 0):
        return redirect("../faculty_dashboard")
    elif(request.session.get('account_type', False) == 1):
        return redirect("../student_dashboard")
    return render(request, 'online_exam/Login.html')

def signup(request):
    #the data from html is being stored and checked here(signup request daali thi tou it will check if the user name and password are correct)
    if(request.method == "POST" and request.POST.get('first_name', False) != False and request.POST.get('last_name', False) != False and request.POST.get('email', False) != False and request.POST.get('phone', False) != False):
        new_user = user(first_name = request.POST['first_name'], last_name = request.POST['last_name'], phone = request.POST['phone'], email = request.POST['email'], password = make_password(request.POST['password']))
        if(user.objects.filter(email=request.POST['email']).exists()):
            error_message = "Email ID already exists!!"
            return render(request, 'online_exam/Signup.html', {"error_message":error_message})
        else:
            new_user.save()
            message = "Account Created Successfully!!"
            return render(request, 'online_exam/Signup.html', {"message":message})
    return render(request, 'online_exam/Signup.html')

def sign_out(request):
    request.session.flush()
    return redirect('../login')

def authenticate(request, token=None):
    clientSecret = "1c616e2f378f9aa90c936b1560e6d0c372fa5e5a54457356f39573955e7e64b445d2f03673a8905088b43c114465020825f48b79e8ce85b0e20e6ad8b736e860"
    Payload = { 'token': token, 'secret': clientSecret }
    k = requests.post("https://serene-wildwood-35121.herokuapp.com/oauth/getDetails", Payload)
    data = json.loads(k.content) 
    print(data['student'][0]['Student_Email'])
    user_email = data['student'][0]['Student_Email']
    if(user.objects.filter(email=user_email).exists() == False):
        new_user = user()
        new_user.first_name = data['student'][0]['Student_First_Name']
        new_user.last_name = data['student'][0]['Student_Last_name']
        new_user.email = data['student'][0]['Student_Email']
        new_user.phone = data['student'][0]['Student_Mobile']
        new_user.password = make_password("iamstudent")
        new_user.save()
    login_user = user.objects.get(email = user_email)
    request.session['id'] = login_user.id
    request.session['first_name'] = login_user.first_name
    request.session['last_name'] = login_user.last_name
    request.session['email'] = login_user.email
    request.session['phone'] = login_user.phone
    request.session['account_type'] = login_user.account_type
    print(data)
    return redirect('login')

def get_exams_by_course(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0 and request.POST.get('course_id', False) != False):
        exams = dict()
        j = 0
        for i in (exam_detail.objects.filter(course_id=course.objects.filter(id = request.POST.get('course_id', False)).all()).values("id", "exam_name")):
            exams[i['id']] = i['exam_name']
            j += 1
        return HttpResponse(json.dumps(exams))
    return HttpResponseNotFound('<h1>Page not found</h1>')

def get_subtopics_by_topic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0 and request.POST.get('topic_id', False) != False):
        subtopics = dict()
        j = 0
        for i in (subtopic.objects.filter(topic_id=topic.objects.filter(id = request.POST.get('topic_id', False)).all()).values("id", "subtopic_name")):
            subtopics[i['id']] = i['subtopic_name']
            j += 1
        return HttpResponse(json.dumps(subtopics))
    return HttpResponseNotFound('<h1>Page not found</h1>')
