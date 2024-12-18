import logging
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
logger = logging.getLogger(__name__)

class MetadataService:
    @classmethod
    def store_metadata(cls, file_id, project_id, metadata):
        """
        Store metadata for a file directly in MongoDB
        """
        try:
            # MongoDB connection
            client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]
            
            # Prepare metadata document
            metadata_doc = {
                'file_id': file_id,
                'project_id': project_id,
                'metadata': metadata,
                'created_at': datetime.utcnow()
            }
            
            # Remove existing metadata for this file
            db.metadata.delete_many({
                'file_id': file_id,
                'project_id': project_id
            })
            
            # Insert new metadata
            result = db.metadata.insert_one(metadata_doc)
            
            client.close()
            
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Metadata storage error: {e}")
            return None

    @classmethod
    def get_metadata(cls, file_id=None, project_id=None):
        """
        Retrieve metadata based on file_id or project_id
        """
        try:
            # MongoDB connection
            client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]
            
            # Build query
            query = {}
            if file_id:
                query['file_id'] = file_id
            if project_id:
                query['project_id'] = project_id
            
            # Retrieve metadata
            metadata = list(db.metadata.find(query))
            
            client.close()
            
            # Convert ObjectId to string
            for item in metadata:
                item['_id'] = str(item['_id'])
            
            return metadata
        
        except Exception as e:
            logger.error(f"Metadata retrieval error: {e}")
            return []