from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from notification_app.models import Notification
from notification_app.api.serializers import NotificationSerializer
from rest_framework import status

class CreateNotificationView(APIView):
    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")

        if not title:
            return Response({"error": "Title is required."}, status=400)

        # Ensure request.user is passed correctly
        notification = Notification.objects.create(
            user=request.user,
            title=title,
            description=description
        )

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=201)
    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")

        if not title:
            return Response({"error": "Title is required."}, status=400)

        # Assign a default user if not authenticated
        user = request.user if request.user.is_authenticated else None

        # Create the notification
        notification = Notification.objects.create(
            user=user,
            title=title,
            description=description
        )

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=201)

class NotificationListView(APIView):
    def get(self, request):
        # Fetch notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
