from uagents import Agent, Context, Model, Protocol
# third party modules used in this example
from pydantic import Field
from ai_engine import UAgentResponse, UAgentResponseType
import random
from vectara_helper_func import create_chat, add_turn
import re


class ResearchSummarizer(Model):
    query_to_knowledge_base: str = Field(description="This field contents the message for the knowledge base (full of research papers)")

agent = Agent()

research_summarizer_protocol = Protocol("ResearchSummarizer")

@research_summarizer_protocol.on_message(model=ResearchSummarizer, replies={UAgentResponse})
async def research(ctx: Context, sender: str, msg: ResearchSummarizer):
    chat_id = ctx.storage.get('chat_id')
    response = await add_turn(chat_id, msg.query_to_knowledge_base, ctx)
    ctx.logger.info(f'Reply from the agent {response}')
    cleaned_response = re.sub(r'\[\d+\]', '', response)
    await ctx.send(sender, UAgentResponse(message=cleaned_response, type=UAgentResponseType.FINAL))

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started: {agent.address}")
    initial_query = 'I want help with my research, summarizing my paper drafts and helping report my results to others'
    chat_id, initial_response = await create_chat(initial_query, ctx)
    ctx.storage.set('chat_id', chat_id)

agent.include(research_summarizer_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()


