from uagents import Agent, Context, Model, Protocol
from pydantic import Field
from ai_engine import UAgentResponse, UAgentResponseType
import requests
import json

# Replace with your actual Groq API key
GROQ_API_KEY = "gsk_E0ZAc5ILe87aQglP3QiqvjssejhgbkjdbugelOk5zSrvINlc75A"

class GradeReportRequest(Model):
    course_name: str = Field(description="The name of the course for which to generate a grade report")

agent = Agent()
grade_report_protocol = Protocol("GradeReporter")

# Static grade data
GRADE_DATA = """
Course: Introduction to Computer Science
Number of Students: 20

Grades (out of 100):
1. 85  2. 92  3. 78  4. 88  5. 95
6. 70  7. 82  8. 90  9. 75  10. 87
11. 93 12. 79 13. 86 14. 91 15. 84
16. 77 18. 89 19. 81 20. 94

Questions with high error rates:
1. What is the time complexity of quicksort in the worst case? (8 students answered incorrectly)
2. Explain the concept of polymorphism in object-oriented programming. (7 students struggled)
3. How does virtual memory work in operating systems? (6 students had difficulty)
"""

def generate_grade_report(course_name, query):
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
                "content": "You are an AI assistant that analyzes and reports on student grades for a professor."
            },
            {
                "role": "user",
                "content": f"Given the following grade data for the course '{course_name}', {query}:\n\n{GRADE_DATA}"
            }
        ],
        "max_tokens": 300
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating grade report: {str(e)}"

@grade_report_protocol.on_message(model=GradeReportRequest, replies={UAgentResponse})
async def report_grades(ctx: Context, sender: str, msg: GradeReportRequest):
    query = "provide a concise report including: 1) concepts students are struggling with based on the questions with high error rates, 2) the highest score, 3) the lowest score, and 4) the mean score of the class. Also, suggest potential areas for improvement in teaching or curriculum."
    response = generate_grade_report(msg.course_name, query)
    ctx.logger.info(f'Reply from Groq API: {response}')
    await ctx.send(sender, UAgentResponse(message=response, type=UAgentResponseType.FINAL))

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started: {agent.address}")
    ctx.logger.info("Grade report agent is ready to process requests.")

agent.include(grade_report_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()