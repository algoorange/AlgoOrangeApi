from dotenv import load_dotenv
from app.domain.interfaces import Agent
import groq
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class GeneralAgent(Agent):
    def __init__(self):
        self.client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

    async def handle_query(self, userChatQuery: str, chatHistory: str):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Use the best available Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant providing general advice.and emotional intelligence model trained on a diverse range of data with emoji .and give a respose like a human with friendly and short responses.",
                },
                {"role": "user", "content": userChatQuery},
                {"role": "user", "content": chatHistory},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
