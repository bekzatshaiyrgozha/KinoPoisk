from django.contrib import admin
from django.urls import path,include
from apps.accounts.views import register_view,login_view,logout_view,home
from apps.accounts import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    

]
