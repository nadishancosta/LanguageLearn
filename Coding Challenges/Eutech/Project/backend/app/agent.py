
import os
import json
import asyncio
import importlib

import re
import pandas as pd
import numpy as np

# Gemini libraries and components
from google.adk.agents import Agent

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.code_executors import BuiltInCodeExecutor

from dotenv import load_dotenv


# Custom imports
from .tools import _load_and_prepare_data
from .cus_prompt import return_instructions

import warnings

warnings.filterwarnings("ignore")

import logging

logging.basicConfig(level=logging.ERROR)


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

AGENT_DATAFRAME = _load_and_prepare_data()
AGENT_MODEL = os.environ["MODEL_NAME"]
AGENT_NAME = "data_analyst_agent_v1"
APP_NAME = "data_analyst"
USER_ID = "user1234"
SESSION_ID = "session_code_exec_async"

data_analyst_agent = Agent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    code_executor=BuiltInCodeExecutor(),
    description="Provides processed data for questions regarding air quality.",
    instruction=return_instructions()
)

print(f"Agent '{data_analyst_agent.name}' created using model '{AGENT_MODEL}'.")




async def call_agent_async(query,runner):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    final_response_text = "No final text response captured."
    last_code = None
    final_response_text = None
    try:
        
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            print(f"Event ID: {event.id}, Author: {event.author}")


            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.executable_code:
                        code = part.executable_code.code
                        last_code = code  # <-- capture latest code chunk
                        print(
                            f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                        )
                        has_specific_part = True
                    elif part.code_execution_result:
                        
                        print(
                            f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                        )
                        has_specific_part = True
                    
                    elif part.text and not part.text.isspace():
                        print(f"  Text: '{part.text.strip()}'")
                        

            
            
            # if not has_specific_part and event.is_final_response():
            #     if (
            #         event.content
            #         and event.content.parts
            #         and event.content.parts[0].text
            #     ):
            #         final_response_text = event.content.parts[0].text.strip()
            #         print(f"Final Agent Response: {final_response_text}")
            #     else:
            #         print("Final Agent Response: [No text content in final event]")
            
            if event.is_final_response():
                if event.content and event.content.parts and event.content.parts[0].text:
                    final_response_text = event.content.parts[0].text.strip()
            
    except Exception as e:
        print(f"ERROR during agent run: {e}")

    print("-" * 30)
    
    code_to_write = None
    if last_code:
        code_to_write = last_code
    elif final_response_text:
        # Try to extract a fenced block if present
        m = re.search(r"```(?:python)?\s*(.*?)```", final_response_text, flags=re.S)
        if m:
            code_to_write = m.group(1).strip()
    
    # try:
        
    #     with open(os.path.join(os.path.dirname(__file__), "generated_script.py"), "w") as file:
    #         file.write(final_response_text[9:-4])
    # except Exception as e:
    #     print(e)
    
    
    

    if not code_to_write:
        raise RuntimeError("No code was produced by the agent.")

    out_path = os.path.join(os.path.dirname(__file__), "generated_script.py")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code_to_write)
    print(f"Wrote generated code to {out_path}")


async def run_prompt(query):
    try:
        
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        runner = Runner(agent=data_analyst_agent, app_name=APP_NAME, session_service=session_service)
        
        await call_agent_async(query,runner)
        
        from . import generated_script
        importlib.reload(generated_script) #ensure latest script is loaded 
        
        df = _load_and_prepare_data()
        
        output_data = generated_script.process_iaq_query(df)
        
        return output_data
    
    # except Exception as e:
    #     return await e

    except Exception as e:
        return {"type": "text", "data": f"Error: {e}"}
    
