from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register_user, name='user-register'),
    path('', views.get_user_list, name='user-list'),
    path('<uuid:user_id>/', views.get_user_detail, name='user-detail'),
    path('<uuid:user_id>/update/', views.update_user, name='user-update'),
    path('<uuid:user_id>/delete/', views.delete_user, name='user-delete'),
]
