from fastapi import APIRouter, FastAPI
from typing import Dict
from app.domain.projectApis.task_service_mongo_implementaion import (
    taskServiceMongoImplementation,
)

app = FastAPI()
taskApiRouter = APIRouter()
tasks_service = taskServiceMongoImplementation()


@taskApiRouter.get("/tasks")
async def get_tasks(tasktIds: str = None):
    projects = await tasks_service.GetTasks(tasktIds)  # Fetch projects
    return projects


@taskApiRouter.post("/tasks")
async def create_tasks(task_data: Dict):
    # Extract project data if wrapped in an additional property
    if len(task_data) == 1 and isinstance(next(iter(task_data.values())), dict):
        task_data = next(iter(task_data.values()))

    return await tasks_service.CreateTasks(task_data)
