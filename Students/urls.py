from django.urls import path
from .views import StudentListAPI, StudentDetailAPI

urlpatterns = [
    path('student/', StudentListAPI.as_view()),
    path('student/<int:student_id>/', StudentDetailAPI.as_view()),
]
