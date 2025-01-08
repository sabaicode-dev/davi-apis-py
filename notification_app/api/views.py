from rest_framework.views import APIView
from rest_framework.response import Response
from notification_app.models import Notification
from notification_app.api.serializers import NotificationSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import UpdateAPIView
from rest_framework import status
from bson import ObjectId 

class CreateNotificationView(APIView):
    def post(self, request):
        file_name = request.data.get("file_name")

        if not file_name:
            return Response({"error": "File name is required."}, status=400)

        # Create the notification
        notification = Notification.objects.create(file_name=file_name)

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=201)


class NotificationPagination(PageNumberPagination):
    page_size = 10  # Number of notifications per page


class NotificationListView(APIView):
    def get(self, request):
        notifications = Notification.objects.all().order_by('-created_at')  # Fetch all notifications
        paginator = NotificationPagination()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MarkNotificationAsReadView(UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def patch(self, request, pk):
        try:
            # Convert pk to ObjectId
            notification = Notification.objects.get(pk=ObjectId(pk))
            notification.is_read = True  # Mark as read
            notification.save()
            return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
