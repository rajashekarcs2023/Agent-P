

from uagents import Agent, Context, Model, Protocol
from pydantic import Field
from ai_engine import UAgentResponse, UAgentResponseType
import requests
import json

# Replace with your actual Groq API key
GROQ_API_KEY = "gsk_E0ZAc5ILe87aQglP3QiqWGdjhvdjcvjhbbadjbcbcca"

class EmailSummarizer(Model):
    date: str = Field(description="The date for which to summarize emails")

agent = Agent()
email_summarizer_protocol = Protocol("EmailSummarizer")

# Static email data
EMAIL_DATA = """
**Email 1 (Student 1):**
Subject: Request for Office Hours Appointment
Dear Professor Smith,
I hope you're doing well. I am struggling with some concepts from last week's lecture, specifically on distributed systems. Could I schedule an office hours appointment to discuss these? I would be available Tuesday or Wednesday afternoon.
Best regards,  
Emily Davis

**Email 2 (Student 2):**
Subject: Clarification on Assignment 3
Dear Professor Smith,
Could you clarify the expectations for Assignment 3? I am unsure about the level of detail required for the algorithm design section. I would appreciate any additional guidance.
Thank you,  
Mark Nguyen

**Email 3 (Student 1):**
Subject: Request for Recommendation Letter
Dear Professor Smith,
I'm applying for a research internship and would be honored if you could provide a recommendation letter. I have attached my resume and project list for your reference. Please let me know if this is possible.
Best,  
Emily Davis

**Email 4 (Department Head 1):**
Subject: Reminder for Semester Grading Deadlines
Dear Professor Smith,
This is a reminder that all grades must be submitted by the end of this week. Kindly ensure that your grading is completed and uploaded to the system by Friday at 5 PM.
Best regards,  
Dr. Karen Watson  
Department Head

**Email 5 (Department Head 2):**
Subject: Upcoming Faculty Meeting Agenda
Dear Faculty,
A quick reminder of the faculty meeting on Thursday at 3 PM. Please review the attached agenda, and come prepared to discuss curriculum updates for the next academic year.
Regards,  
Dr. Thomas Lee  
Assistant Dean
"""

def generate_summary(date, query):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that summarizes email content for a professor."
            },
            {
                "role": "user",
                "content": f"Given the following emails received on {date}, {query}:\n\n{EMAIL_DATA}"
            }
        ],
        "max_tokens": 250
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@email_summarizer_protocol.on_message(model=EmailSummarizer, replies={UAgentResponse})
async def summarize_emails(ctx: Context, sender: str, msg: EmailSummarizer):
    query = "provide a concise summary of the key points"
    response = generate_summary(msg.date, query)
    ctx.logger.info(f'Reply from Groq API: {response}')
    await ctx.send(sender, UAgentResponse(message=response, type=UAgentResponseType.FINAL))

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started: {agent.address}")
    ctx.logger.info("Email summarizer agent is ready to process requests.")

agent.include(email_summarizer_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()