import os
import json
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

import openai

from vand import VandBasicAPITool

'''
1. Get a ToolPack (e.g. Weather)
2. Send a request that needs the tool (e.g. what's the weather like in Florida)
3. Get function call
4. execute function
5. return funciton results to model

'''

openai.api_key = os.getenv("OPENAI_API_KEY")
# or set your key with 
# openai.api_key = "sk-..."

if openai.api_key is None:
    print("Did you forget to set your OpenAI API Key? e.g. export OPENAI_API_KEY='sk-...' ")

GPT_MODEL = "gpt-3.5-turbo-1106"


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


# get the weather ToolPack from Vand.io
# find more toolpacs at https://vand.io/toolpacks
# just replace the Vand ID ("vand-.*") with the Vand ID of the tool you want to use.
get_weather = VandBasicAPITool.get_toolpack("vand-6657ac86-b112-4776-a5cc-fae3aa80ba56")


messages = []
messages.append({"role": "system", "content": "Answer user questions as best you can.  Find and use a tool to increase accuracy or add capabilites if needed."})
messages.append({"role": "user", "content": "What's the weather like in Honolulu today?"})

chat_response = chat_completion_request(messages, get_weather.functions) # functions included in request
assistant_message = chat_response.json()["choices"][0]["message"]
messages.append(assistant_message)

if assistant_message.get("function_call"):
    # execute the function and get a tuple of the function output and any tools (functions)
    toolMessage, toolPack = VandBasicAPITool.execute_function_call(assistant_message)
    # put the function output into the chat history
    messages.append({"role": "function", "name": assistant_message["function_call"]["name"], "content": toolMessage})
    # provide chat history and the results of the function call to the model
    chat_response = chat_completion_request(messages,  toolPack)
    assistant_message = chat_response.json()["choices"][0]["message"]
    messages.append(assistant_message)

pretty_print_conversation(messages)

