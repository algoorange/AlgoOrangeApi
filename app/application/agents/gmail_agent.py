import base64
from email.mime.text import MIMEText
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.domain.interfaces import Agent
from google.oauth2 import service_account
import os
import groq  # Groq's API
from dotenv import load_dotenv  # Import dotenv to load environment variables

# Load environment variables from .env file
load_dotenv()

# OAuth 2.0 credentials
CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
SERVICE_ACCOUNT_FILE = r"C:\Algo Orange\algoorangeapi\gmail_credentials.json"
SCOPES = ["https://mail.google.com/"]


class GmailAgent(Agent):
    def _init_(self):
        # Initialize credentials using OAuth 2.0
        self.creds = Credentials(
            None,
            refresh_token=REFRESH_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

    async def handle_query(self, userChatQuery: str, userChatHistory: str) -> str:
        client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

        # Query Groq LLM to determine which agent to call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that determines which email action to perform.",
                },
                {
                    "role": "user",
                    "content": f"Query: {userChatQuery}. Identify if the query is related to one of the following actions:"
                    "read → If the query is about reading emails,"
                    "send → If the query is about sending an email."
                    "Respond with only one word from the list: read or send. Do not provide explanations.",
                },
            ],
            max_tokens=10,
        )

        # query_lower = response.choices[0].message["content"].strip().lower()
        query_lower = response.choices[0].message.content.strip().lower()

        if query_lower == "read":
            return await self.read_and_reply_emails()
        elif query_lower == "send":
            return await self.send_email(userChatQuery)
        else:
            return "Unknown query type."

    async def read_and_reply_emails(self) -> str:
        try:
            service = build("gmail", "v1", credentials=self.creds)
            results = (
                service.users().messages().list(userId="me", maxResults=5).execute()
            )
            messages = results.get("messages", [])

            if not messages:
                return "No emails found."

            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                    .execute()
                )
                headers = msg["payload"]["headers"]
                subject = next(
                    (
                        header["value"]
                        for header in headers
                        if header["name"] == "Subject"
                    ),
                    "No Subject",
                )
                sender = next(
                    (header["value"] for header in headers if header["name"] == "From"),
                    "Unknown Sender",
                )
                body = self.get_email_body(msg)

                if (
                    sender != "samitalgoexercises2025@gmail.com"
                ):  # Avoid replying to yourself
                    reply_body = self.generate_reply(body)
                    await self.replay_send_email(sender, f"Re: {subject}", reply_body)

            return "Replies sent successfully."
        except HttpError as error:
            print(f"An error occurred: {error}")
            return f"Error reading and replying to emails: {error}"

    def get_email_body(self, msg):
        """Extracts the email body from the message."""
        payload = msg["payload"]
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
        return "No email body found."

    def generate_reply(self, email_body: str) -> str:
        """Generates a reply to the email using Groq LLM."""
        client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

        # Query Groq LLM to determine which agent to call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI email assistant that generates appropriate replies.",
                },
                {
                    "role": "user",
                    "content": f"Email received: {email_body}. Generate a polite and professional reply.",
                },
            ],
            max_tokens=4000,
        )
        return response.choices[0].message.content.strip()

    async def replay_send_email(self, to: str, subject: str, body: str) -> str:
        """Sends an email reply using OAuth 2.0 credentials."""
        try:
            # Use the OAuth 2.0 credentials (self.creds)
            service = build("gmail", "v1", credentials=self.creds)

            # Create the email message
            message = {"raw": self.create_message(to, subject, body)}

            # Send the email
            service.users().messages().send(userId="me", body=message).execute()
            return f"Reply sent to {to}."
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return f"Error sending email: {str(e)}"

    async def send_email(self, userChatQuery: str) -> str:
        """Sends an email reply using OAuth 2.0 credentials."""
        to, subject = self.extract_email_details(
            userChatQuery
        )  # Extract email details from the query
        body = self.generate_email_body(userChatQuery)  # Generate email body using LLM
        try:
            # Use the OAuth 2.0 credentials (self.creds)
            service = build("gmail", "v1", credentials=self.creds)

            # Create the email message
            message = {"raw": self.create_message(to, subject, body)}

            # Send the email
            service.users().messages().send(userId="me", body=message).execute()
            return f"Reply sent to {to}."
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return f"Error sending email: {str(e)}"

    def extract_email_details(self, userChatQuery: str):
        client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that extracts email details from user queries. "
                        "Extract the recipient email address, subject of the email."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Query: {userChatQuery}\n"
                    "Extract and return the following fields:\n"
                    "- 'to' (recipient email)\n"
                    "- 'subject'\n"
                    "Respond with *raw JSON only*. Do not use markdown or explanations.",
                },
            ],
            max_tokens=200,
        )

        try:
            content = response.choices[0].message.content.strip()

            # Remove markdown fences if present
            content = re.sub(r"^json|$", "", content).strip()

            # Now parse as JSON
            email_details_dict = json.loads(content)
            to = email_details_dict.get("to", "recipient@example.com")
            subject = email_details_dict.get("subject", "No Subject")
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            to, subject = "recipient@example.com", "Error Subject"
        return to, subject

    def create_message(self, to, subject, body):
        """Creates an encoded email message."""
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        return base64.urlsafe_b64encode(message.as_bytes()).decode()

    def generate_email_body(self, userChatQuery: str) -> str:
        """
        Generate an email body using an LLM based on the user query.
        """
        client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

        # Query the LLM to generate the email body
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that generates email bodies based on user queries. "
                        "Write a professional and polite email body based on the given query."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Query: {userChatQuery}\n" "Generate a detailed and  .",
                },
            ],
            max_tokens=500,
        )

        try:
            body = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating email body: {e}")
            body = "Error generating email body."

        return body
