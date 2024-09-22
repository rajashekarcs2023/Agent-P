from uagents import Agent, Context, Model, Protocol
from pydantic import Field
from ai_engine import UAgentResponse, UAgentResponseType
import requests
import json

# Replace with your actual Groq API key
GROQ_API_KEY = "gsk_E0ZAc5ILe87aQvhfsjhbfhjbzbcaGelOk5zSrvINlc75A"

class ClassPlanRequest(Model):
    lecture_date: str = Field(description="The date for which to prepare the class plan")

agent = Agent()
class_plan_protocol = Protocol("ClassPlanner")

# Static lecture notes data
LECTURE_NOTES = """
Dr. Al Gorithm Lecture Notes
AI Agents
September 22, 2024

What are agents?
- Explain the definition
- What confusion do people have
- Why are people concerned

What is the history of agents?
- Review the history

Agents in the LLM Era
- How are agents used today

How do agents work?
- Explain the concepts of planning, iteration, multi agents, actions

Autonomous Agents

Risk Frameworks

LangGraph

Lang Observability
- Arize
- LangSmith

Gaurdrails
"""

def generate_class_plan(lecture_date, query):
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
                "content": "You are an AI assistant that helps professors prepare comprehensive class plans and homework assignments."
            },
            {
                "role": "user",
                "content": f"Based on the following lecture notes for the class on {lecture_date}, {query}:\n\n{LECTURE_NOTES}"
            }
        ],
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating class plan: {str(e)}"

@class_plan_protocol.on_message(model=ClassPlanRequest, replies={UAgentResponse})
async def prepare_class_plan(ctx: Context, sender: str, msg: ClassPlanRequest):
    query = "provide a comprehensive class plan, and homework assignment with 10 multiple-choice questions and a written question."
    response = generate_class_plan(msg.lecture_date, query)
    ctx.logger.info(f'Reply from Groq API: {response}')
    await ctx.send(sender, UAgentResponse(message=response, type=UAgentResponseType.FINAL))

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started: {agent.address}")
    ctx.logger.info("Class planner agent is ready to process requests.")

agent.include(class_plan_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()