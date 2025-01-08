from django.urls import path
from .views import CreateNotificationView, NotificationListView, MarkNotificationAsReadView

urlpatterns = [
    path('create/', CreateNotificationView.as_view(), name='notification-create'),
    path('list/', NotificationListView.as_view(), name='notification-list'),
    path('mark-as-read/<str:pk>/', MarkNotificationAsReadView.as_view(), name='mark-notification-as-read'),  # Changed <int:pk> to <str:pk>
]
