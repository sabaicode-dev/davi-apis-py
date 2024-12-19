import logging
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime
from metafile.api.services.data_cleaning import convert_numpy_types

logger = logging.getLogger(__name__)

class MetadataService:
    def __init__(self):
        try:
            self.client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            self.db = self.client[settings.DATABASES['default']['NAME']]
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            raise

    def close_connection(self):
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()

    def store_metadata(self, file_id, project_id, metadata):
        """
        Store metadata in the database.

        Args:
            file_id (str): The ID of the file.
            project_id (str): The ID of the project.
            metadata (dict): Metadata to store.

        Returns:
            str or None: The ID of the inserted document, or None if an error occurred.
        """
        try:
            # Convert numpy types before storing
            converted_metadata = convert_numpy_types(metadata)

            # Prepare the document to be stored
            metadata_doc = {
                "file_id": file_id,
                "project_id": project_id,
                "metadata": converted_metadata,
                "created_at": datetime.utcnow(),
            }

            # Insert the document into the database
            result = self.db.metadata.insert_one(metadata_doc)
            return str(result.inserted_id) if result.inserted_id else None

        except PyMongoError as e:
            logger.error(f"Error storing metadata in MongoDB: {e}")
            return None

        finally:
            self.close_connection()

    def get_metadata(self, file_id=None, project_id=None):
        """
        Retrieve metadata based on file_id or project_id.

        Args:
            file_id (str, optional): The ID of the file. Defaults to None.
            project_id (str, optional): The ID of the project. Defaults to None.

        Returns:
            list: A list of metadata documents matching the query.
        """
        try:
            # Build query
            query = {}
            if file_id:
                query['file_id'] = file_id
            if project_id:
                query['project_id'] = project_id

            # Retrieve metadata from the database
            metadata = list(self.db.metadata.find(query))

            # Convert ObjectId to string for JSON serialization
            for item in metadata:
                item['_id'] = str(item['_id'])

            return metadata

        except PyMongoError as e:
            logger.error(f"Error retrieving metadata from MongoDB: {e}")
            return []

        finally:
            self.close_connection()

    @staticmethod
    def convert_object_ids(metadata):
        """
        Convert ObjectId to string for JSON serialization.

        Args:
            metadata (list): List of metadata documents.

        Returns:
            list: Metadata documents with `_id` fields converted to strings.
        """
        for item in metadata:
            if '_id' in item:
                item['_id'] = str(item['_id'])
        return metadata

    def get_metadata_by_id(self, metadata_id):
        try:
            if not ObjectId.is_valid(metadata_id):
                logger.debug("Invalid metadata_id format: %s", metadata_id)
                return None  # Invalid format

            object_id = ObjectId(metadata_id)
            logger.debug("Searching for metadata with _id: %s", object_id)

            # Retrieve metadata from the database
            metadata = self.db.metadata.find_one({"_id": object_id})

            if metadata:
                # Convert ObjectId to string for JSON serialization
                metadata['_id'] = str(metadata['_id'])
                logger.debug("Metadata found: %s", metadata)
                return metadata  # This will be a dict with _id as string
            else:
                logger.debug("No metadata found with _id: %s", object_id)
                return None
        except Exception as e:
            logger.exception("Error retrieving metadata by ID")
            return None