from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from bson import ObjectId
from app.infrastructure.db.mongo_db import db
from app.domain.projectApis.project_service_interfaces import ProjectServiceInterface
from fastapi.encoders import jsonable_encoder  # Import for sanitizing input data


class ProjectServiceMongoImplementation:
    async def GetProjects(self, projectIds: Optional[str] = None) -> List[Dict]:
        """
        Fetch projects from MongoDB.
        - If `projectIds` is provided, fetch only those projects.
        - Otherwise, fetch all projects.
        """
        collection = db["projects"]  # Access the 'projects' collection

        query = {}  # Default query to fetch all projects

        if projectIds:
            try:
                # Convert comma-separated IDs into a list of ObjectIds
                project_ids_list = [ObjectId(pid) for pid in projectIds.split(",")]
                query = {"_id": {"$in": project_ids_list}}
            except Exception:
                return {
                    "error": "Invalid ObjectId format"
                }  # Handle invalid ObjectId input

        # Query MongoDB
        cursor = collection.find(query)
        projects = await cursor.to_list(length=None)

        # Convert ObjectId fields in all documents
        def convert_objectid(doc):
            """Recursively converts ObjectId to string in nested dictionaries and lists"""
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        return [convert_objectid(project) for project in projects]

    async def GetProjectsByProgram(self, programIds: str) -> List[Dict[str, Any]]:
        """
        Fetch projects associated with specific program IDs.
        """
        collection = db["projects"]  # Access the 'projects' collection

        query = {}  # Default query to fetch all projects

        if programIds:
            try:
                # Convert comma-separated IDs into a list of ObjectIds
                project_ids_list = [ObjectId(pid) for pid in programIds.split(",")]
                query = {"program_id": {"$in": project_ids_list}}
            except Exception:
                return {
                    "error": "Invalid ObjectId format"
                }  # Handle invalid ObjectId input

        # Query MongoDB
        cursor = collection.find(query)
        projects = await cursor.to_list(length=None)

        # Convert ObjectId fields in all documents
        def convert_objectid(doc):
            """Recursively converts ObjectId to string in nested dictionaries and lists"""
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        return [convert_objectid(project) for project in projects]

    async def GetProjectsByPortfolio(self, portfolioIds: str) -> List[Dict[str, Any]]:
        """
        Fetch projects associated with specific portfolio IDs.
        - Requires `portfolioIds` as a comma-separated string.
        - Returns only projects linked to the given portfolio IDs.
        """
        collection = db["projects"]  # Ensure querying the correct collection

        if not portfolioIds:
            raise HTTPException(
                status_code=400, detail="Portfolio IDs are required"
            )  # ✅ Mandatory check

        try:
            # Convert the comma-separated portfolio IDs into a list of ObjectIds
            portfolio_ids_list = [ObjectId(pid) for pid in portfolioIds.split(",")]
        except Exception:
            raise HTTPException(
                status_code=400, detail="Invalid ObjectId format"
            )  # ✅ Proper error handling

        # Query MongoDB for projects linked to the provided portfolio IDs
        cursor = collection.find({"portfolio_id": {"$in": portfolio_ids_list}})
        projects = await cursor.to_list(length=None)

        if not projects:
            return []  # ✅ Returns an empty list if no projects are found

        def convert_objectid(doc):
            """Recursively converts ObjectId to string in nested dictionaries and lists"""
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        return [
            convert_objectid(project) for project in projects
        ]  # ✅ Convert ObjectIds to strings

    async def CreateProject(self, project_data: Dict) -> Dict:
        """
        Implementation of CreateProject to insert a new project into MongoDB.
        """
        collection = db["projects"]

        # Sanitize input data to ensure it is JSON-serializable
        try:
            project_data = jsonable_encoder(project_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid input data: {str(e)}")

        result = await collection.insert_one(project_data)
        project_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        return project_data
