from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/log/', views.log_action, name='log_action'),
    path('api/log', views.log_action),
    path('api/ping/', views.ping, name='ping'),
    path('api/ping', views.ping),
    path('api/meetings/', views.meetings, name='meetings'),
    path('api/meetings', views.meetings),
    path('api/meetings/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('api/meetings/<int:meeting_id>', views.meeting_detail),
    path('api/meetings/<int:meeting_id>/photos/', views.meeting_photos, name='meeting_photos'),
    path('api/meetings/<int:meeting_id>/photos', views.meeting_photos),
    path('api/meetings/<int:meeting_id>/photos/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('api/meetings/<int:meeting_id>/photos/<int:photo_id>', views.delete_photo),
    path('api/auth/status/', views.auth_status, name='auth_status'),
    path('api/auth/status', views.auth_status),
    path('api/auth/login/', views.auth_login, name='auth_login'),
    path('api/auth/login', views.auth_login),
    path('api/auth/logout/', views.auth_logout, name='auth_logout'),
    path('api/auth/logout', views.auth_logout),
]