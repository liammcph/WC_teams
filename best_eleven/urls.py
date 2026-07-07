"""
URL configuration for best_eleven project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    # Linking in URLs from the Djangos Auth Project
    path('accounts/', include('django.contrib.auth.urls'))
]

"""
URLs the Auth project provides

/login/ [name='login']
/logout/ [name='logout']
/password_change/ [name='password_change']
/password_change/done/ [name='password_change_done']
/password_reset/ [name='password_reset']
/password_reset/done/ [name='password_reset_done']
/reset/<uidb64>/<token>/ [name='password_reset_confirm']
/reset/done/ [name='password_reset_complete']

"""
