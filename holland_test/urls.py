from django.urls import path
from . import views

app_name = 'holland_test'

urlpatterns = [
    path('', views.holland_test_start, name='start'),        # /holland/
    path('take/', views.holland_test_take, name='take'),     # /holland/take/
    path('result/<int:result_id>/', views.holland_test_result, name='result'),
    path('history/', views.holland_test_history, name='history'),
]