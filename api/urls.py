from django.urls import path
from home.views import doctor_API,patient_API,date_API
from home.views import doctor_update_API,doctor_partial_update_API,doctor_delete_API
from home.views import patient_update_API,patient_partial_update_API,patient_delete_API,patient_search_API,patient_filter_API
from home.views import date_update_API,date_delete_API

urlpatterns = [
    # get post
    path('patient/', patient_API),
    path('doctor/', doctor_API),
    path('date/',date_API),
    path('search/<str:query>/', patient_search_API ),
    path('search/<str:query>/<str:recovered>/', patient_filter_API ),

    # update delete
    path('doctor/<int:pk>/', doctor_update_API),
    path('doctor/partial/<int:pk>/', doctor_partial_update_API),
    path('doctor/delete/<int:pk>/', doctor_delete_API),

    path('patient/<int:pk>/', patient_update_API),
    path('patient/partial/<int:pk>/', patient_partial_update_API),
    path('patient/delete/<int:pk>/', patient_delete_API),

    path('date/<int:pk>/', date_update_API),
    path('date/delete/<int:pk>/', date_delete_API),
]
