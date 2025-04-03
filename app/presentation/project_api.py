from fastapi import APIRouter, FastAPI
from typing import Dict
from app.domain.projectApis.project_service_mongo_implementation import (
    ProjectServiceMongoImplementation,
)

app = FastAPI()
projectApiRouter = APIRouter()
project_service = ProjectServiceMongoImplementation()


@projectApiRouter.get("/projects")
async def get_projects(projectIds: str = None):
    projects = await project_service.GetProjects(projectIds)  # Fetch projects
    return projects


@projectApiRouter.post("/projects")
async def create_project(project_data: Dict):
    # Extract project data if wrapped in an additional property
    if len(project_data) == 1 and isinstance(next(iter(project_data.values())), dict):
        project_data = next(iter(project_data.values()))

    return await project_service.CreateProject(project_data)


@projectApiRouter.get("/projects/programs")
async def get_projects_by_program(programIds: str):
    return await project_service.GetProjectsByProgram(programIds)


@projectApiRouter.get("/projects/portfolios")
async def get_projects_by_portfolio(portfolioIds: str):
    return await project_service.GetProjectsByPortfolio(portfolioIds)
