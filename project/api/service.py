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
        """
        Create a new project instance
        """
        try:
            # Ensure required fields are present in the data
            project_name = data.get("project_name")
            if not project_name:
                raise ValueError("Project name is required.")
    
            project_description = data.get("project_description", "")  # Default to empty string if not provided
            deleted_at = data.get("deleted_at", None)
    
            # Create the project instance
            project = Project(
                project_name=project_name,
                project_description=project_description,
                deleted_at=deleted_at
            )
            
            # Save the project and catch potential database errors
            try:
                project.save()
                logger.info(f"Project created successfully: {project.project_name}")
                return project
            except Exception as db_error:
                logger.error(f"Database error while creating project: {str(db_error)}")
                raise Exception(f"Database error: {str(db_error)}")
                
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise ValueError(str(ve))
        except Exception as e:
            logger.exception("Error creating project")
            raise Exception(f"Error creating project: {str(e)}")


    @staticmethod
    def get_project_by_id(project_id):
        """
        Retrieve a project instance by ID
        """
        try:
            if not ObjectId.is_valid(project_id):
                logger.debug("Invalid project_id format: %s", project_id)
                return None  # Invalid format

            # Convert project_id to ObjectId
            object_id = ObjectId(project_id)
            logger.debug("Searching for project with _id: %s", object_id)
            project = Project.objects.filter(_id=object_id).first()
            print("ObjectId: ",project)
            if project:
                logger.debug("Project found: %s", project)
            else:
                logger.debug("No project found with _id: %s", object_id)
            return project
        except Exception as e:
            logger.exception("Error retrieving project by ID")
            return None
    
    @staticmethod
    def update_project(project_id,data):
        """
        Update an existing project
        """
        try:
            project = ProjectService.get_project_by_id(project_id)
            if not project:
                return None
            
            project.project_name = data.get("project_name",project.project_name)
            project.project_description = data.get("project_description",project.project_description)
            project.save()
            return project
        except Exception as e:
            logger.exception("Error update project")
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
        Retrieve all projects with filters, sorting, and pagination.
        """
        try:
            queryset = Project.objects.all()
            
            # Apply filters if provided
            if filters:
                queryset = queryset.filter(**filters)
            
            # Apply sorting if provided
            if sort_by:
                # Determine ascending or descending order
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