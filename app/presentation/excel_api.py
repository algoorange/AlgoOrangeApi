from fastapi import FastAPI, APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.application.orchestrator.use_cases import Orchestrator

app = FastAPI()
excelRouter = APIRouter()


# Define a Pydantic model for the request body
class excelrequest(BaseModel):
    data: str
    userQuery: Optional[str] = (None,)
    chatHistory: Optional[str] = (None,)


@excelRouter.post("/query")
async def handle_request(request: excelrequest):
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


app.include_router(excelRouter)  # Corrected to use the router object
