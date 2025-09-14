import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError
from mongo_connection import get_collection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB objects"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def get_approved_events() -> List[Dict[str, Any]]:
    try:       
        collection = get_collection("events")
        
        cursor = collection.find(
            {"status": "approved"}
        ).sort("startTime", 1)
        
        events = list(cursor)  # Convert cursor to list
        return events
        
    except (PyMongoError, Exception) as e:
        logger.error(f"Error fetching events: {str(e)}")
        return []

def lambda_handler(event, context):
    try:
        logger.info("Attempting to connect to MongoDB and fetch documents.")
        events = get_approved_events()
        logger.info(f"Fetched {len(events)} events")
        
        return {
            'statusCode': 200,
            'body': json.dumps(events, cls=JSONEncoder)  # Use custom encoder
        }
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
