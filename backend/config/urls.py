from django.urls import include, path

urlpatterns = [
    path('api/auth/', include('auth.api.urls')),
    path('api/users/', include('users.api.urls')),
    path('api/access/', include('access.api.urls')),
    path('mock/', include('mock.urls')),
]
