from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from bson import ObjectId
from app.infrastructure.db.mongo_db import db
from app.domain.projectApis.task_service_interfaces import TaskServiceInterface
from fastapi.encoders import jsonable_encoder  # Import for sanitizing input data

class taskServiceMongoImplementation:
    async def GetTasks(self, tasktIds: Optional[str] = None) -> List[Dict]:
        """
        Fetch tasks from MongoDB.
        - If `tasktIds` is provided, fetch only those tasks.
        - Otherwise, fetch all tasks.
        """
        collection = db["tasks"]  # Access the 'tasks' collection

        query = {}  # Default query to fetch all tasks

        if tasktIds:
            try:
                # Convert comma-separated IDs into a list of ObjectIds
                task_ids_list = [ObjectId(pid) for pid in tasktIds.split(",")]
                query = {"_id": {"$in": task_ids_list}}
            except Exception:
                return {"error": "Invalid ObjectId format"}  # Handle invalid ObjectId input

        # Query MongoDB
        cursor = collection.find(query)
        tasks = await cursor.to_list(length=None)

        # Convert ObjectId fields in all documents
        def convert_objectid(doc):
            """ Recursively converts ObjectId to string in nested dictionaries and lists """
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        return [convert_objectid(project) for project in tasks]    
    
    async def CreateTasks(self, task_data: Dict) -> Dict:
        """
        Implementation of CreateProject to insert a new project into MongoDB.
        """
        collection = db["tasks"]

        # Sanitize input data to ensure it is JSON-serializable
        try:
            task_data = jsonable_encoder(task_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid input data: {str(e)}")

        result = await collection.insert_one(task_data)
        task_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        return task_data



