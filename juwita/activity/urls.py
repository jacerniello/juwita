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
    path('api/meetings/<int:meeting_id>/', views.delete_meeting, name='delete_meeting'),
    path('api/meetings/<int:meeting_id>', views.delete_meeting),
]