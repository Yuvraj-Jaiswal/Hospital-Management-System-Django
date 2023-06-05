from django.db.models import Q
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.shortcuts import render,redirect
from rest_framework import status
from .models import Doctor,Patient,PDates
from .serializers import DoctorSerializer , PatientSerializer , PDateSerializer
from django.contrib.auth import authenticate, login , logout
from .forms import MyCreateUserForm , MyPasswordResetForm
from django.contrib import messages
from datetime import datetime
from django.conf import settings
from email.message import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
import smtplib
import requests
import re



def hospital(request):
    if not request.user.is_authenticated:
        return redirect('/')

    # patients_data = requests.get("http://localhost:8000/api/patient/")
    doctor = Doctor.objects.get(username=request.user.username)
    patients_data = Patient.objects.filter(doctor=doctor.id).order_by('-id')

    if request.method == 'POST' and 'search_form' in request.POST:
        query = request.POST['query']
        # patients_data = requests.get(f"http://localhost:8000/api/search/?q={request.POST['query']}")

        if request.POST['clicked_button']=='all':
            patients_data = Patient.objects.filter(Q(firstName__icontains=query) |
                                                   Q(lastName__icontains=query) |
                                                   Q(disease__icontains=query))

        elif request.POST['clicked_button']=='rec':
            patients_data = Patient.objects.filter((Q(firstName__icontains=query) |
                                                   Q(lastName__icontains=query) |
                                                   Q(disease__icontains=query) ) & Q(cured = True))

        elif request.POST['clicked_button']=='nrec':
            patients_data = Patient.objects.filter(( Q(firstName__icontains=query) |
                                                     Q(lastName__icontains=query) |
                                                     Q(disease__icontains=query) ) & Q(cured = False))

        return render(request , 'hospital.html',{"patients_data" : patients_data , "search" : query , "clicked_button" : request.POST['clicked_button']})

    return render(request , 'hospital.html',{"patients_data" : patients_data , "search" : '' , "clicked_button" : "all"})


def checkMail(email:str):
    count = email.count(".")
    double_dot = email.count("..")
    re_pattern = r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$"
    if re.match(re_pattern, email) and email[-1] != "." and email[-2] != "." and len(email) > 0 and double_dot == 0 and count <= 2:
        return True
    else: return False


def isChar(string):
    if string.isalpha(): return True
    return False


def create_pat(request):
    if not request.user.is_authenticated:
        return redirect('/')

    doctor_obj = Doctor.objects.get(username=request.user.username)

    if request.method == 'POST':
        data = request.POST

        if isChar(data['firstName']) is False:
            messages.error(request, "Invalid first name - Name should only consist characters")
            return render(request, 'createPatient.html', {"doctor": doctor_obj, "info": data})

        if isChar(data['lastName']) is False:
            messages.error(request, "Invalid last name - Name should only consist characters")
            return render(request, 'createPatient.html', {"doctor": doctor_obj, "info": data})

        if len(data['phone']) != 10:
            messages.error(request,"Invalid phone number")
            return render(request , 'createPatient.html', {"doctor" : doctor_obj , "info" : data})

        if checkMail(data['email']) is False:
            messages.error(request, "Invalid email")
            return render(request , 'createPatient.html', {"doctor" : doctor_obj , "info" : data})

        response = requests.post("http://localhost:8000/api/patient/",data)
        if response.status_code == 201:
            try:
                return redirect('/hospital')
            except Exception as e:
                print(e)
                messages.error(request, "invalid user")
                return redirect("/create")

    return render(request , 'createPatient.html', {"doctor" : doctor_obj})


def update_pat(request,pk):
    if not request.user.is_authenticated:
        return redirect('/')

    pat_obj = Patient.objects.get(id=pk)

    if request.method == 'POST' and 'update_form' in request.POST:
        data = request.POST

        if isChar(data['firstName']) is False:
            messages.error(request, "Invalid first name - Name should only consist characters")
            return render(request , 'updatePatient.html', {"patient" : pat_obj})

        if isChar(data['lastName']) is False:
            messages.error(request, "Invalid last name - Name should only consist characters")
            return render(request , 'updatePatient.html', {"patient" : pat_obj})

        if len(data['phone']) != 10:
            messages.error(request,"invalid phone number")
            return render(request , 'updatePatient.html', {"patient" : pat_obj})

        if checkMail(data['email']) is False:
            messages.error(request, "invalid email")
            return render(request , 'updatePatient.html', {"patient" : pat_obj})

        response = requests.put(f"http://localhost:8000/api/patient/{pk}/",data)

        if response.status_code == 200:
            return redirect('/hospital')

    return render(request , 'updatePatient.html', {"patient" : pat_obj})


def patient_detail(request,pk):
    if not request.user.is_authenticated:
        return redirect('/')

    pat_obj = Patient.objects.get(id=pk)
    dates = PDates.objects.filter(patient=pk)

    return render(request , 'patientDetail.html', {"patient" : pat_obj , "dates" : dates})


def delete_pat(request,pk):
    if not request.user.is_authenticated:
        return redirect('/')

    # response = requests.delete(f"http://localhost:8000/api/patient/delete/{pk}/")
    patient = Patient.objects.get(id=pk)
    patient.delete()
    return redirect('/hospital')


def scheduleDate(request,pk):
    if not request.user.is_authenticated:
        return redirect('/')

    pat_obj = Patient.objects.get(id=pk)
    if request.method == 'POST' and 'schedule' in request.POST:
        input_date = request.POST['date']
        parsed_date = datetime.strptime(input_date, '%Y-%m-%dT%H:%M')
        readable_date = parsed_date.strftime('%B %d, %Y %I:%M %p')
        current_date = datetime.now()

        if datetime.strptime(input_date, '%Y-%m-%dT%H:%M') > current_date:
            new_date = PDates(date=input_date, patient=pat_obj)
            new_date.save()

            message = EmailMessage()
            message_data = f"Hi {request.POST['firstName']} {request.POST['lastName']} " \
                           f"your next appointment from crucial hospital is scheduled on {readable_date} please be there on time."
            message['From'] = settings.EMAIL_HOST_USER
            message['To'] = pat_obj.email
            message['Subject'] = "Crucial Hospital Appointment"
            message.set_content(message_data)
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            username = settings.EMAIL_HOST_USER
            password = settings.EMAIL_HOST_PASSWORD

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                try:
                    server.starttls()
                    server.login(username, password)
                    server.send_message(message)
                except Exception as e:
                    print(e)

            return redirect('/hospital')

        else:
            messages.error(request,"Enter correct date for appointment")
            return redirect(f'/schedule/{pk}')

    return render(request , 'dateSchedular.html' , {"patient" : pat_obj})


# AUTH


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset_link = request.build_absolute_uri('/reset_pass/') + token + f"/{email}/"

            message = EmailMessage()
            message_data = f'Click the following link to reset your password: {reset_link}'

            message['From'] = settings.EMAIL_HOST_USER
            message['To'] = email
            message['Subject'] = "Crucial Hospital Password Reset Link"
            message.set_content(message_data)
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            username = settings.EMAIL_HOST_USER
            password = settings.EMAIL_HOST_PASSWORD

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                try:
                    server.starttls()
                    server.login(username, password)
                    server.send_message(message)
                except Exception as e:
                    print(e)

            messages.success(request, 'Password reset email sent. Check your inbox.')
            return redirect('/')

        except User.DoesNotExist:
            messages.error(request, 'Invalid Email or Email does not registered.')

    return render(request, 'forgot_password.html')



def reset_password(request, token , email):
    try:
        user = User.objects.get(email=email)
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(user, token):
            if request.method == 'POST':
                form = MyPasswordResetForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Password reset successfully.')
                    return redirect('/')
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{error}")
                    return render(request, 'reset_password.html', {'form': form})
            else:
                form = MyPasswordResetForm(user)


            return render(request, 'reset_password.html', {'form': form})

        else:
            messages.error(request, 'Invalid token.')
            return redirect('/')

    except User.DoesNotExist:
        messages.error(request, 'Invalid token or User does not exists.')
        return redirect('/')


def doctor_login(request):
    if request.user.is_authenticated:
        return redirect('/hospital')

    if request.method == "POST":
        username , password =  request.POST['username'] , request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/hospital')
        else:
            messages.error(request,"Enter Correct Username or Password")
            return redirect("/")
    else:
        return render(request , 'login.html')


def doctor_register(request):
    if request.user.is_authenticated:
        return redirect('/hospital')

    if request.method == 'POST':
        data = request.POST
        form = MyCreateUserForm(request.POST)

        print(data)

        try:
            Doctor.objects.get(email=request.POST['email'])
            messages.error(request, "Email already exists for another user")
            return render(request , 'register.html' , {'form' : form})
        except Exception as e:
            print(e)
            pass

        if isChar(data['first_name']) is False:
            messages.error(request, "Invalid first name - Name should only consist characters")
            return render(request , 'register.html' , {'form' : form})

        if isChar(data['last_name']) is False:
            messages.error(request, "Invalid last name - Name should only consist characters")
            return render(request , 'register.html' , {'form' : form})

        if checkMail(request.POST['email']) is False:
            messages.error(request, "Invalid email")
            return render(request , 'register.html' , {'form' : form})

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(request,username=username,password=password)
            if user is not None:
                login(request, user)
                data = request.POST
                response = requests.post("http://localhost:8000/api/doctor/", data)
                if response.status_code == 200 or response.status_code == 201:
                    return redirect('/hospital')
            else:
                messages.error(request, "Authentication Failed")
                return render(request , 'register.html' , {'form' : form})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

            return render(request , 'register.html' , {'form' : form})
    else:
        form = MyCreateUserForm()

    return render(request , 'register.html' , {'form' : form})

def doctor_logout(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            logout(request)
            return redirect("/")
    return redirect("/hospital")



# APIS


@csrf_exempt
@api_view(['GET', 'POST'])
def doctor_API(request):
    if request.method == 'GET':
        objs = Doctor.objects.all()
        json_data = DoctorSerializer(objs, many=True)
        return Response(json_data.data)

    elif request.method == 'POST':
        data = request.data
        json_data = DoctorSerializer(data=data)
        if json_data.is_valid():
            json_data.save()
            return Response(json_data.data,status=201)
        else:
            return Response(json_data.errors,status=400)


@csrf_exempt
@api_view(['GET','PUT'])
def doctor_update_API(request, pk):
    if request.method == 'GET':
        try:
            obj = Doctor.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = DoctorSerializer(obj)
        return Response(json_data.data, status=200)

    if request.method == 'PUT':
        try:obj = Doctor.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = DoctorSerializer(obj, data=request.data)
        if json_data.is_valid():
            json_data.save()
            return Response(json_data.data,status=200)
        else:
            return Response(json_data.errors,status=400)



@csrf_exempt
@api_view(['PATCH'])
def doctor_partial_update_API(request, pk):
    try:obj = Doctor.objects.get(id=pk)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)

    json_data = DoctorSerializer(obj, data=request.data , partial=True)
    if json_data.is_valid():
        json_data.save()
        return Response(json_data.data,status=200)
    else:
        return Response(json_data.errors,status=400)

@csrf_exempt
@api_view(['DELETE'])
def doctor_delete_API(request, pk):
    try:obj = Doctor.objects.get(id=pk)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)

    obj.delete()
    return Response(f"deleted {pk}")

# end doctor api

# patient api

@csrf_exempt
@api_view(['GET', 'POST'])
def patient_API(request):
    if request.method == 'GET':
        objs = Patient.objects.all()
        json_data = PatientSerializer(objs, many=True)
        return Response(json_data.data)

    elif request.method == 'POST':
        data = request.data
        json_data = PatientSerializer(data=data)
        if json_data.is_valid():
            json_data.save()
            return Response(json_data.data,status=201)
        else:
            return Response(json_data.errors,status=400)


@csrf_exempt
@api_view(['GET','PUT'])
def patient_update_API(request, pk):
    if request.method == 'GET':
        try:
            obj = Patient.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = PatientSerializer(obj)
        return Response(json_data.data, status=200)


    if request.method == 'PUT':
        try:obj = Patient.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = PatientSerializer(obj, data=request.data)
        if json_data.is_valid():
            json_data.save()
            return Response(json_data.data,status=200)
        else:
            return Response(json_data.errors,status=400)

@csrf_exempt
@api_view(['PATCH'])
def patient_partial_update_API(request, pk):
    try:obj = Patient.objects.get(id=pk)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)

    json_data = PatientSerializer(obj, data=request.data , partial=True)
    if json_data.is_valid():
        json_data.save()
        return Response(json_data.data,status=200)
    else:
        return Response(json_data.errors,status=400)

@csrf_exempt
@api_view(['GET'])
def patient_search_API(request,query):
    patients = Patient.objects.all()
    results = patients.filter(
        Q(firstName__icontains=query) |
        Q(lastName__icontains=query) |
        Q(disease__icontains=query)
    )
    json_data = PatientSerializer(results , many=True)
    return Response(json_data.data)

@csrf_exempt
@api_view(['GET'])
def patient_filter_API(request,query,recovered):

    if recovered == 'true':
        try:
            patients_data = Patient.objects.filter((Q(firstName__icontains=query) |
                                                    Q(lastName__icontains=query) |
                                                    Q(disease__icontains=query)) & Q(cured=True))
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)


    elif recovered == 'false':
        try:
            patients_data = Patient.objects.filter((Q(firstName__icontains=query) |
                                                    Q(lastName__icontains=query) |
                                                    Q(disease__icontains=query)) & Q(cured=False))
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        try:
            patients_data = Patient.objects.filter(Q(firstName__icontains=query) |
                                                   Q(lastName__icontains=query) |
                                                   Q(disease__icontains=query))
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

    json_data = PatientSerializer(patients_data , many=True)
    return Response(json_data.data)


@csrf_exempt
@api_view(['DELETE'])
def patient_delete_API(request, pk):
    try:
        obj = Patient.objects.get(id=pk)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)

    obj.delete()
    return Response(f"deleted {pk}")

# end patient api

# date api

@csrf_exempt
@api_view(['GET','POST'])
def date_API(request):
    if request.method == 'GET':
        objs = PDates.objects.all()
        json_data = PDateSerializer(objs,many=True)
        return Response(json_data.data)

    elif request.method == 'POST':
        data = request.data
        json_data = PDateSerializer(data=data)
        if json_data.is_valid():
            json_data.save()
            return Response(json_data.data,status=201)
        else:
            return Response(json_data.errors,status=400)


@csrf_exempt
@api_view(['GET','PUT'])
def date_update_API(request, pk):

    if request.method == 'GET':
        try:
            obj = PDates.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = PDateSerializer(obj)
        return Response(json_data.data, status=200)

    if request.method == 'PUT':
        try:
            obj = PDates.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = PDateSerializer(obj, data=request.data)
        if json_data.is_valid():
            json_data.save()
            return Response(json_data.data,status=200)
        else:
            return Response(json_data.errors,status=400)

@csrf_exempt
@api_view(['DELETE'])
def date_delete_API(request, pk):
    try:
        obj = PDates.objects.get(id=pk)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)

    obj.delete()
    return Response(f"deleted {pk}")

# end date api


