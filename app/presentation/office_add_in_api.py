from fastapi import FastAPI, APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.application.agents.ms_excel_agent import MSExcelAgent
from app.application.orchestrator.use_cases import Orchestrator

app = FastAPI()
officePluginRouter = APIRouter()


# Define a Pydantic model for the request body
class MSOfficeAddInModel(BaseModel):
    data: str
    userQuery: Optional[str] = (None,)
    chatHistory: Optional[str] = (None,)


@officePluginRouter.post("/excel")
async def handle_request(request: MSOfficeAddInModel):
    # Process the request data
    print(f"Request received: data={request.data}")
    # Process user query using Orchestrator if userQuestion is provided
    if request.userQuery:

        agentVal = await MSExcelAgent().handle_query(request.userQuery, request.data, request.chatHistory)        
        
        response = agentVal
    else:
        response = "No user question provided."

    return {"message": response}


@officePluginRouter.post("/word")
async def handle_request(request: MSOfficeAddInModel):
    # Process the request data
    print(f"Request received: data={request.data}")
    # Process user query using Orchestrator if userQuestion is provided
    if request.userQuery:
        orchestrator = Orchestrator(
            userChatQuery=request.userQuery,
            chatHistory=request.chatHistory,
            data=request.data,
        )
        response = await orchestrator.route_query()
    else:
        response = "No user question provided."

    return {"message": response}


@officePluginRouter.post("/outlook")
async def handle_request(request: MSOfficeAddInModel):
    # Process the request data
    print(f"Request received: data={request.data}")
    # Process user query using Orchestrator if userQuestion is provided
    if request.userQuery:
        orchestrator = Orchestrator(
            userChatQuery=request.userQuery,
            chatHistory=request.chatHistory,
            data=request.data,
        )
        response = await orchestrator.route_query()
    else:
        response = "No user question provided."

    return {"message": response}


app.include_router(officePluginRouter)  # Corrected to use the router object
