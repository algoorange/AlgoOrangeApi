from fastapi import APIRouter, FastAPI
from typing import Dict

from app.domain.projectApis.program_service_mongo_implementation import (
    ProgramServiceMongoImplementation,
)

app = FastAPI()
programApiRouter = APIRouter()
program_service = ProgramServiceMongoImplementation()

# -------------------------------
# 📌 Get All Collection Names
# -------------------------------


@programApiRouter.get("/program")
async def get_programs(programIds: str = None):
    return await program_service.GetPrograms(programIds)


@programApiRouter.post("/program")
async def create_program(program_data: Dict):
    # Extract project data if wrapped in an additional property
    if len(program_data) == 1 and isinstance(next(iter(program_data.values())), dict):
        program_data = next(iter(program_data.values()))

    return await program_service.CreateProgram(program_data)


@programApiRouter.get("/program/portfolios")
async def get_projects_by_portfolio(portfolioIds: str):
    return await program_service.GetProgramByPortfolio(portfolioIds)
