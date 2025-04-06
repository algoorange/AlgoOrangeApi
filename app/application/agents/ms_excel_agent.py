import json
from typing import Optional
from app.domain.interfaces import Agent
import groq  # Groq's API


class MSExcelAgent(Agent):
    def __init__(self):
        # Initialize Groq client
        self.client = groq.Client(
            api_key="GROQ_API_KEY"
        )

    def format_data(self, data: str) -> str:
        """
        Format the input JSON data into a structured summary for the LLM.
        :param data: JSON string containing Excel data.
        :return: A formatted string summarizing the data.
        """
        try:
            # Parse the JSON data
            parsed_data = json.loads(data)

            # Check if the data is empty
            if not parsed_data:
                return "No data provided."

            # Build a summary dynamically
            summary = "Summary of Excel Data:\n"
            for i, entry in enumerate(parsed_data):
                summary += f"Row {i + 1}:\n"
                for key, value in entry.items():
                    summary += f"  {key}: {value}\n"

                # Limit the number of rows summarized (e.g., first 10 rows)
                if i >= 9:
                    summary += "\n(Note: Only the first 10 rows are summarized.)"
                    break

                return summary
        except json.JSONDecodeError:
            return "Invalid JSON data provided."
        except Exception as e:
            return f"Error formatting data: {e}"

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
                        "content": "You are an AI that processes Excel data and answers the user queries. On the result privide only the answer to the user question.",
                    },
                    {
                        "role": "user",
                        "content": f"Data: {data}. Query: {userChatQuery}. Chat History: {userChatHistory}.",
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
