from django.urls import path
from . import views

urlpatterns = [
    # home page
    path('', views.index, name='index'),        
    # button API    
    path('api/log/', views.log_action, name='log_action'),  
]