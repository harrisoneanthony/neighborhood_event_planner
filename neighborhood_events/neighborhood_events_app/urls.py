from django.urls import path     
from . import views

urlpatterns = [
    path('', views.register),
    path('login/', views.login),
    path('login_user',views.login_user),
    path('register/', views.register),
    path('dashboard/<int:id>', views.dashboard),
    path('create_user', views.create_user),
    path('logout', views.logout),   
]
