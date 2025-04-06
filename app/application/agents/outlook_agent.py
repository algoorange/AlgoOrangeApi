from typing import Optional
import requests
import os
import json
import groq
from app.domain.interfaces import Agent

class OutlookAgent(Agent):
    def __init__(self):
        self.client_id = os.getenv("OUTLOOK_CLIENT_ID")
        self.client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")
        self.tenant_id = os.getenv("OUTLOOK_TENANT_ID")
        self.access_token = self.get_access_token()

        # Initialize Groq API client
        self.groq_client = groq.Client(api_key="GROQ_API_KEY")

    def get_access_token(self):
        """Retrieve an access token using OAuth 2.0."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": "M.C555_BL2.2.U.44ba755a-17c9-3282-f3aa-b45f616df2a8",
            "redirect_uri": "https://localhost:8000",
            "scope": "https://graph.microsoft.com/.default offline_access"
        }
        response = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(f"Error retrieving access token: {response.json()}")

    async def handle_query(self, userChatQuery: str, userChatHistory: str,userContent: Optional[str] = None) -> str:
        """Determines whether to read or reply to emails."""
        query_type = "read"  # Default action for now
        if query_type == "read":
            return await self.read_and_reply_to_emails()
        else:
            return "Unknown query type."

    async def read_and_reply_to_emails(self) -> str:
        """Fetch unread emails, generate replies, and send responses."""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get("https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false&$top=5",
                                    headers=headers)
            response.raise_for_status()
            emails = response.json().get("value", [])

            if not emails:
                return "No unread emails found."

            for email_data in emails:
                sender_email = email_data["from"]["emailAddress"]["address"]
                subject = email_data["subject"]
                body = self.extract_email_body(email_data)

                print(f"Analyzing email from {sender_email} - Subject: {subject}")

                # Generate AI-powered reply
                # reply_content = self.generate_reply(body)
                reply_content = "Hai"

                # Send the reply
                self.send_email_reply(sender_email, subject, reply_content, email_data["id"])

            return f"Processed {len(emails)} emails and sent replies."

        except Exception as e:
            return f"Error reading emails: {str(e)}"

    def extract_email_body(self, email_data):
        """Extract the email body as plain text."""
        body = email_data.get("body", {}).get("content", "")
        return body if body else "No email body available."

    def generate_reply(self, email_body):
        """Uses Groq API to analyze the email and generate a reply."""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that writes professional email replies."},
                    {"role": "user", "content": f"Analyze the email and draft a professional reply: {email_body}"}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating reply: {e}")
            return "Sorry, I couldn't generate a response at this moment."

    def send_email_reply(self, recipient, original_subject, reply_body, message_id):
        """Send an email reply to the original sender."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            reply_data = {
                "message": {
                    "subject": f"Re: {original_subject}",
                    "body": {
                        "contentType": "Text",
                        "content": reply_body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": recipient}}
                    ]
                },
                "comment": "Replying to your email."
            }

            # Send reply using Microsoft Graph API
            url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/reply"
            response = requests.post(url, headers=headers, data=json.dumps(reply_data))

            if response.status_code == 202:
                print(f"Reply sent successfully to {recipient}")
            else:
                print(f"Failed to send reply: {response.json()}")

        except Exception as e:
            print(f"Error sending email reply: {e}")
