from typing import Optional
from dotenv import load_dotenv
from app.domain.interfaces import Agent
import groq
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class SocialMediaAgent(Agent):
    def __init__(self):
        self.client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

    async def handle_query(self, userChatQuery: str, chatHistory: str,userContent: Optional[str] = None):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Use the best available Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant providing medical advice. with an emotional intelligence model trained on a diverse range of social media and trending uo to date  data.give a respose like a human with friendly and short responses.",
                },
                {"role": "user", "content": userChatQuery},
                {"role": "user", "content": chatHistory},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
