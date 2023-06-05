from django.urls import path
from .views import hospital,doctor_register,doctor_login,\
    doctor_logout,create_pat,delete_pat,update_pat,patient_detail,scheduleDate,forgot_password,reset_password

urlpatterns = [
    path('' , doctor_login),
    path('register/' , doctor_register),
    path('hospital/' , hospital),
    path('logout/' , doctor_logout),
    path('create/' , create_pat),
    path('schedule/<int:pk>/' , scheduleDate),
    path('detail/<int:pk>/' , patient_detail),
    path('update/<int:pk>/', update_pat),
    path('delete/<int:pk>/', delete_pat),
    path('forget_pass/', forgot_password),
    path('reset_pass/<str:token>/<str:email>/', reset_password),
]