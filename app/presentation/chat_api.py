from fastapi import FastAPI, APIRouter
from app.application.orchestrator.use_cases import Orchestrator
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
chatRouter = APIRouter()


@chatRouter.get("/query")
async def query_handler(userChatQuery: str):

    # Process user query using Orchestrator
    orchestrator = Orchestrator(userChatQuery)
    response = await orchestrator.route_query()
    return {
        "response": response,
    }


app.include_router(chatRouter)
