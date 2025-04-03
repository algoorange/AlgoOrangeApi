import json
import os
import re
from app.domain.interfaces import Agent
from app.infrastructure.services.vector.vector_store import retrieve_relevant_text
from app.domain.projectApis.project_service_mongo_implementation import (
    ProjectServiceMongoImplementation,
)
import groq
from fastapi.encoders import jsonable_encoder
from openai import OpenAI

project_service = ProjectServiceMongoImplementation()


class ProjectAgent(Agent):
    def __init__(self):
        """Initialize the LLM client"""
        self.client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

    async def handle_query(self, userChatQuery, chatHistory):
        """Handles user queries by detecting intent and processing accordingly."""
        intent = self.detect_intent(userChatQuery)

        if intent == "create_project":
            project_data = self.get_project_details(userChatQuery, chatHistory)

            if not self.is_project_data_complete(project_data):
                missing_fields = self.get_missing_fields(project_data)
                followup_query = self.ask_followup_questions(missing_fields)
                return followup_query  # Ask user for missing details

            wrapped_data = self.wrap_project_data(project_data)
            response = await self.create_project_api(wrapped_data)
            return response  # Return API response

        else:  # Default to retrieving project details
            return self.retrieve_project_details(userChatQuery, chatHistory)

    def detect_intent(self, user_query):
        """Identifies whether the user wants to create a project or get details."""
        prompt = (
            f"User Query: {user_query}\n"
            "Identify the user's intent and respond with only one of the following:\n"
            "- 'create_project' if the user wants to create a new project.\n"
            "- 'get_project_details' if the user wants details about an existing project.\n"
            "Respond with only one of these two words."
        )
        response = self.query_llm(prompt)
        return response.strip().lower()

    def get_project_details(self, user_query, chatHistory):
        """Extracts required details for creating a project."""
        prompt = (
            f"User Query: {user_query}, Chat History: {chatHistory}\n"
            "Extract the following fields from the query:\n"
            "- name\n"
            "- description\n"
            "- department_id\n"
            "- portfolio_id\n"
            "- program_id\n"
            "- funding_source\n"
            "- total_budget\n"
            "- status\n"
            "- start_date\n"
            "- end_date\n"
            "- created_by\n"
            "Respond with a JSON object containing the extracted values.no extra text, just the JSON object."
        )
        response = self.query_llm(prompt)
        try:
            # Remove Markdown JSON code block markers (```json ... ```)
            cleaned_response = re.sub(r"```json|```", "", response).strip()

            # Remove newlines and tabs
            cleaned_response = (
                cleaned_response.replace("\n", " ").replace("\t", " ").strip()
            )

            # Parse cleaned JSON
            project_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            project_data = {}

        print("Parsed Project Data:", project_data)  # Debugging Output
        return project_data

    def is_project_data_complete(self, project_data):
        required_fields = [
            "name",
            "description",
            "department_id",
            "portfolio_id",
            "program_id",
            "funding_source",
            "total_budget",
            "status",
            "start_date",
            "end_date",
            "created_by",
        ]
        return all(
            field in project_data and project_data[field] for field in required_fields
        )

    def get_missing_fields(self, project_data):
        required_fields = [
            "name",
            "description",
            "department_id",
            "portfolio_id",
            "program_id",
            "funding_source",
            "total_budget",
            "status",
            "start_date",
            "end_date",
            "created_by",
        ]
        return [field for field in required_fields if not project_data.get(field)]

    def ask_followup_questions(self, missing_fields):
        prompt = (
            f"The user wants to create a project but is missing the following details: {', '.join(missing_fields)}.\n"
            "Ask a follow-up question to get the missing details."
        )
        response = self.query_llm(prompt)
        return response  # Return follow-up question

    def wrap_project_data(self, project_data):
        wrapped_data = {
            "name": project_data.get("name", ""),
            "description": project_data.get("description", ""),
            "department_id": project_data.get("department_id", ""),
            "portfolio_id": project_data.get("portfolio_id", ""),
            "program_id": project_data.get("program_id", ""),
            "funding_source": project_data.get("funding_source", ""),
            "total_budget": project_data.get("total_budget", 0),
            "status": project_data.get("status", "Pending"),
            "start_date": project_data.get("start_date", ""),
            "end_date": project_data.get("end_date", ""),
            "created_by": project_data.get("created_by", ""),
        }
        return wrapped_data

    async def create_project_api(self, project_data):
        """Sends the project data to the CreateProject API and returns the response."""
        project_data = jsonable_encoder(project_data)
        response = await project_service.CreateProject(project_data)
        return response

    def retrieve_project_details(self, userChatQuery, chatHistory):
        """Handles retrieval of project details."""
        retrieved_data = retrieve_relevant_text(userChatQuery)
        if not isinstance(retrieved_data, list):
            retrieved_data = [retrieved_data]
        formatted_context = "\n".join(
            (
                f"- {item.get('collection_name', 'Unknown')}: {item.get('description', item.get('risk_description', item.get('name', 'No description available')))}"
                if isinstance(item, dict)
                else f"- {item}"
            )
            for item in retrieved_data
        )
        prompt = (
            f"Question: {userChatQuery}\n"
            f"Chat History: {chatHistory}\n"
            f"Context:\n{formatted_context}\n"
            f"Answer:"
        )
        response = self.query_llm(prompt)
        return response

    def query_llm(self, prompt):
        """Sends the prompt to LLM and returns the response."""
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant for project management.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
