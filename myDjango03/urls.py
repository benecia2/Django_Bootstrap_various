"""
URL configuration for myDjango03 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# 셋팅
from myapp03 import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.list),
    path('write_form/', views.write_form),
    path('insert/', views.insert),
    path('list/', views.list),
    path('list_page/', views.list_page),

    path('wordcloud/', views.wordcloud),
    path('wordcloud2/', views.wordcloud2),
    path('melon/', views.melon),
    path('map/', views.map),
    path('movie_chart/', views.movie_chart),
    path('movie/', views.movie),
    path('movie_dbchart/', views.movie_dbchart),
    path('weather/', views.weather),


    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup),

]
