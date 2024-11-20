from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from project.api.service import ProjectService
from project.api.serializers import ProjectSerializer
from bson import ObjectId
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore
import logging

logger = logging.getLogger(__name__)

class CreateProject(APIView):
    def post(self, request):
        try:
            project_data = request.data
            project_name = project_data.get("project_name")
            if not project_name:
                return Response(
                    {"error": "Project name is required!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                project = ProjectService.create_project(project_data)
                serializer = ProjectSerializer(project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as ve:
                return Response(
                    {"error": str(ve)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.exception("Error in CreateProject view")
            return Response(
                {"error": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ProjectDetailView(APIView):
    def get(self, request, project_id):
        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not ObjectId.is_valid(project_id):
            return Response({"error": "Invalid project ID format"}, status=status.HTTP_400_BAD_REQUEST)

        project = ProjectService.get_project_by_id(project_id)
        if project:
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

class UpdateProject(APIView):
    def put(self, request, project_id):
        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not ObjectId.is_valid(project_id):
            return Response({"error": "Invalid project ID format"}, status=status.HTTP_400_BAD_REQUEST)

        project = ProjectService.update_project(project_id, request.data)
        if project:
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Project not found or failed to update"}, status=status.HTTP_404_NOT_FOUND)

class DeleteProject(APIView):
    def delete(self, request, project_id):
        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not ObjectId.is_valid(project_id):
            return Response({"error": "Invalid project ID format"}, status=status.HTTP_400_BAD_REQUEST)

        success = ProjectService.delete_project(project_id)
        if success:
            return Response({"message": "Project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Project not found or failed to delete"}, status=status.HTTP_404_NOT_FOUND)

class ListProject(APIView):
    def get(self, request):
        try:
            # Get query parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            sort_by = request.query_params.get('sort_by')
            
            # Validate pagination parameters
            if page < 1 or page_size < 1:
                return Response(
                    {"error": "Invalid pagination parameters"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get projects with pagination
            projects, total_count, total_pages = ProjectService.get_all_project(
                sort_by=sort_by,
                page=page,
                page_size=page_size
            )
            
            # Serialize the results
            serializer = ProjectSerializer(projects, many=True)
            
            response_data = {
                'results': serializer.data,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error listing projects")
            return Response(
                {"error": "Failed to retrieve projects"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )