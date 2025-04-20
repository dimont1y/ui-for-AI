import os
import json
import asyncio
import logging
import uuid
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import Agent, Runner, TResponseInputItem, ItemHelpers, trace, GuardrailFunctionOutput, InputGuardrail, WebSearchTool, RunItemStreamEvent
from api_client.coinmarketcap_api_tool import get_crypto_data, compare_crypto_data, get_historical_data
from api_client.get_token_inf_from_contract import explore_token

load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO)

app = FastAPI()

class Request(BaseModel):
    messages: list[TResponseInputItem]

class MovieOutput(BaseModel):
    reasoning: str
    related_to_movies: bool


class CryptoOutput(BaseModel):
    reasoning: str
    is_about_crypto: bool


guardrails_agent = Agent(
name="Guardrails Agent",
instructions="User's questions should relate to crypto."
    "Greetings are OK. NO homework questions. "
    "Answer with `is_about_crypto=True` if the query is about cryptocurrencies. "
    "Otherwise, set `is_about_crypto=False`.",
output_type=CryptoOutput
)

async def crypto_guardrail(ctx, agent, input_data):
    context_data = getattr(ctx, "context", None)
    result = await Runner.run(guardrails_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(CryptoOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_about_crypto
    )

crypto_assistant_agent = Agent(
    name="Crypto Assistant Agent",
    handoff_description="A specialist that knows crypto currencies cost and can tell the info about them.",
    instructions="You should be able to tell the user the cost of a crypto currency. You can tell the cost of it "
                 "in USD or in BTC.",
    tools=[get_crypto_data, compare_crypto_data],
    input_guardrails = [InputGuardrail(guardrail_function=crypto_guardrail)]
)

analytics_agent = Agent(
    name="Analytics Agent",
    handoff_description="A specialist that analyzes and compares cryptocurrencies.",
    instructions="Use available tools to compare and analyze crypto prices and trends.",
    tools=[get_crypto_data, compare_crypto_data]
)

web_search_agent = Agent(
    name="Web Search Agent",
    handoff_description="A specialist that can search the web for information about crypto. Trigger this agent when "
                        "user asks for information about certain coin or cryptocurrency.",
    instructions="You can search the web for information about a specific coin, cryptocurrency, or anything else. Always do web searches. ",
    tools=[WebSearchTool(search_context_size="high")]
)

historical_data_agent = Agent(
    name="Historical Data Agent",
    handoff_description="Агент для отримання історичних даних про криптовалюту.",
    instructions="Якщо користувач запитує про історичну динаміку криптовалюти, використовуйте інструмент `get_historical_data`.",
    tools=[get_historical_data]
    )

token_explorer_agent = Agent(
    name="Token Explorer Agent",
    handoff_description="Агент для аналізу токенів у різних мережах: ETH, BSC, Solana.",
    instructions="Перевіряй інформацію про токени за адресою контракту. Визнач мережу за контекстом або запитай користувача.",
    tools=[explore_token]
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You are a specialist that greets the user and delegates tasks to other agents based on the user's question. ",
    handoffs=[crypto_assistant_agent, web_search_agent, analytics_agent, historical_data_agent, token_explorer_agent],
    input_guardrails=[InputGuardrail(guardrail_function=crypto_guardrail)]
)

async def stream_agent_events(input_text: str):
    thread_id = uuid.uuid4().hex
    try:
        result_stream = Runner.run_streamed(triage_agent, input=input_text)
        message_output_created = False
        async for event in result_stream.stream_events():
            if isinstance(event, RunItemStreamEvent):
                logging.info(f"name of event: {event.name}")
                if event.name == 'tool_output':
                    message_output_created = True
            if not message_output_created:
                continue
            if event.type == "raw_response_event":
                try:
                    delta_text = event.data.delta
                    logging.info(f"raw delta token: {delta_text}")
                except AttributeError:
                    delta_text = None
                if delta_text:
                    logging.info(f"Delta token: {delta_text}")
                    yield f'0:{json.dumps(delta_text)}\n'
    except Exception as e:
         logging.error(f"Exception in stream_agent_events: {e}")
         yield '0:"...Sorry, can\'t help with that request!"'

@app.post("/api/chat")
async def handle_chat_data(request: Request):
    try: 
        response = StreamingResponse(stream_agent_events(request.messages))
        response.headers['x-vercel-ai-data-stream'] = 'v1'
        return response
    except:
        return StreamingResponse(iter([f'0:"...Sorry, can\'t help with that request!"']), media_type="text/event-stream")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)