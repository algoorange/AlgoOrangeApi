from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from bson import ObjectId
from app.infrastructure.db.mongo_db import db

class ProgramServiceMongoImplementation:
    async def GetPrograms(self, programIds: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch programs from MongoDB.
        - If `programIds` is provided, fetch only those programs.
        - Otherwise, fetch all programs.
        """
        collection = db["programs"]  
        query = {}

        if programIds:
            try:
                program_ids_list = [ObjectId(pid) for pid in programIds.split(",")]
                query = {"_id": {"$in": program_ids_list}}
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid ObjectId format")

        cursor = collection.find(query)
        programs = await cursor.to_list(length=None)

        def convert_objectid(doc):
            """ Convert ObjectId fields to string in nested dictionaries and lists """
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        return [convert_objectid(program) for program in programs]


    async def GetProgramByPortfolio(self, portfolioIds: str) -> List[Dict[str, Any]]:
        """
        Fetch programs associated with specific portfolio IDs.
        """
        collection = db["programs"]  

        if not portfolioIds:
            raise HTTPException(status_code=400, detail="Portfolio IDs are required")  

        try:
            portfolio_ids_list = [ObjectId(pid) for pid in portfolioIds.split(",")]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")  

        cursor = collection.find({"portfolio_id": {"$in": portfolio_ids_list}})
        programs = await cursor.to_list(length=None)

        if not programs:
            return []  
  
        def convert_objectid(doc):
            """ Convert ObjectId fields to string in nested dictionaries and lists """
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        return [convert_objectid(program) for program in programs]  


    async def CreateProgram(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new program into the 'program' collection in MongoDB.
        """
        collection = db["programs"]  

        # Required fields validation
        required_fields = ["name", "description", "manager_id", "start_date", 
                           "end_date", "portfolio_id"]
        for field in required_fields:
            if field not in program_data or not program_data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Sanitize and encode input
        try:
            program_data = jsonable_encoder(program_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid input data: {str(e)}")

        # Insert into the database
        result = await collection.insert_one(program_data)
        program_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        
        return {"message": "Program created successfully", "program": program_data}
