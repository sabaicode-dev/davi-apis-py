from bson import ObjectId
from project.models import Project
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.utils import timezone
from django.db.models import F


logger = logging.getLogger(__name__)

class ProjectService:
    @staticmethod
    def create_project(data):
        try:
            user_cognito_id = data.get("user_cognito_id")
            if not user_cognito_id:
                raise ValueError("User ID is required.")
            
            project_name = data.get("project_name")
            if not project_name:
                raise ValueError("Project name is required.")

            project_description = data.get("project_description", "")

            # Create the project instance
            project = Project(
                user_cognito_id=user_cognito_id,  # Ensure the user ID is stored
                project_name=project_name,
                project_description=project_description
            )

            # Save to the database
            project.save()
            return project
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise ValueError(str(ve))
        except Exception as e:
            logger.exception("Error creating project")
            raise Exception(f"Error creating project: {str(e)}")





    @staticmethod
    def get_project_by_id(project_id):
        """
        Retrieve a project instance by ID, excluding soft-deleted projects.
        """
        try:
            if not ObjectId.is_valid(project_id):
                logger.debug("Invalid project_id format: %s", project_id)
                return None  # Invalid format

            # Convert project_id to ObjectId
            object_id = ObjectId(project_id)
            logger.debug("Searching for project with _id: %s", object_id)

            # Exclude projects with a non-null deleted_at field
            project = Project.objects.filter(_id=object_id, deleted_at__isnull=True).first()

            if project:
                logger.debug("Project found: %s", project)
            else:
                logger.debug("No project found with _id: %s", object_id)
            return project
        except Exception as e:
            logger.exception("Error retrieving project by ID")
            return None

    
    @staticmethod
    def update_project(project_id, data):
        """
        Update an existing project, ensuring it's not soft-deleted.
        """
        try:
            project = ProjectService.get_project_by_id(project_id)
            if not project:
                return None  # Project not found or soft-deleted

            # Update fields
            project.project_name = data.get("project_name", project.project_name)
            project.project_description = data.get("project_description", project.project_description)
            project.save()
            return project
        except Exception as e:
            logger.exception("Error updating project")
            return None

        

    def delete_project(project_id):
        """
        Soft delete a project instance by setting deleted_at.
        """
        try:
            # Get the project by ID
            project = ProjectService.get_project_by_id(project_id)

            if project:
                # Set the deleted_at timestamp to the current time for soft deletion
                project.deleted_at = timezone.now()
                project.save()  # Save the project with the updated deleted_at field
                return True

            return False
        except Exception as e:
            logger.exception("Error deleting project")
            return False
        
    @staticmethod
    def get_all_project(filters=None, sort_by=None, page=1, page_size=10):
        """
        Retrieve all projects with filters, sorting, and pagination, excluding soft-deleted projects.
        """
        try:
            queryset = Project.objects.filter(deleted_at__isnull=True)  # Exclude soft-deleted projects

            # Apply filters if provided
            if filters:
                queryset = queryset.filter(**filters)

            # Apply sorting if provided
            if sort_by:
                if sort_by.startswith('-'):
                    queryset = queryset.order_by(F(sort_by[1:]).desc())  # descending order
                else:
                    queryset = queryset.order_by(F(sort_by).asc())  # ascending order

            # Get total count for pagination
            total_count = queryset.count()

            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size

            # Get paginated results
            projects = list(queryset[start:end])

            # Calculate total pages
            total_pages = (total_count + page_size - 1) // page_size

            return projects, total_count, total_pages
        except Exception as e:
            logger.exception("Error retrieving projects")
            return [], 0, 0
