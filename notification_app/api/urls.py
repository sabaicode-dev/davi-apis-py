from django.urls import path
from .views import CreateNotificationView, NotificationListView

urlpatterns = [
    path('create/', CreateNotificationView.as_view(), name='notification-create'),
    path('list/', NotificationListView.as_view(), name='notification-list'),
]
