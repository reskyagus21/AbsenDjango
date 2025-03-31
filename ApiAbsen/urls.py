# face_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.capture_page, name='capture_page'),
    path('absen/', views.absen_page, name='absen_page'),
    path('attendance-list/', views.attendance_list_page, name='attendance_list_page'),
    path('api/save-face/', views.save_face, name='save_face'),
    path('api/train-faces/', views.train_faces_view, name='train_faces'),
    path('api/recognize-attend/', views.recognize_and_attend, name='recognize_attend'),
    path('api/today-attendances/', views.get_today_attendances, name='today_attendances'),
    path('api/delete-attendance/', views.delete_attendance, name='delete_attendance'),
    path('api/delete-person/', views.delete_person, name='delete_person'),
    path('api/edit-person/', views.edit_person, name='edit_person'),
]