import json
from app.domain.interfaces import Agent
import groq  # Groq's API


class MSWordAgent(Agent):
    def __init__(self):
        # Initialize Groq client
        self.client = groq.Client(
            api_key="GROQ_API_KEY"
        )

    async def handle_query(
        self, data: str, userChatQuery: str, userChatHistory: str
    ) -> str:

        # Example: Process the Excel data
        print(f"Processing Excel data: {data}")
        print(f"User query: {userChatQuery}")
        print(f"Chat history: {userChatHistory}")

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Replace with the appropriate model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI that processes the content of Microsoft work document and answers the user queries. On the result privide only the answer to the user question.",
                    },
                    {
                        "role": "user",
                        "content": f"Microsoft work document content : {data}. User Query: {userChatQuery}. Chat History: {userChatHistory}.",
                    },
                ],
            )
            llm_response = response.choices[
                0
            ].message.content  # Adjust based on the actual response format
            print(f"LLM Response: {llm_response}")
            return llm_response

        except Exception as e:
            print(f"Error while communicating with Groq LLM: {e}")
            return "Error processing the query with Groq LLM."
