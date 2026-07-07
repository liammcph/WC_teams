from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('teams/', views.team_index, name='team-index'),
    path('teams/<int:team_id>/', views.team_detail, name='team-detail'),
    path('teams/create/', views.TeamCreate.as_view(), name='team-create'),
    path('teams/<int:pk>/update/', views.TeamUpdate.as_view(), name='team-update'),
    path('teams/<int:pk>/delete/', views.TeamDelete.as_view(), name='team-delete'),
    path('teams/<int:team_id>/add-player/<int:player_id>/', views.add_player, name='add-player'),
    path('teams/<int:team_id>/remove-player/<int:player_id>/', views.remove_player, name='remove-player'),
    path('accounts/signup/', views.signup, name='signup'),
]
