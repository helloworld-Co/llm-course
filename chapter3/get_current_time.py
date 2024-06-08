import requests
import os
from openai import OpenAI
import json


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


def get_current_time(timezone: str):
    url = "http://worldtimeapi.org/api/timezone/{tz}"
    rsp = requests.get(url.format(tz=timezone))
    content = json.loads(rsp.text)
    return content.get("datetime")


available_functions = {
    "get_current_time": get_current_time,
}


def run():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get current time based on timezone",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Standard timezone name, ie. America/Los_Angeles, Asia/Shanghai, etc",
                        },
                    },
                    "required": ["timezone"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "What is current time in San Francisco?",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    print("tool_calls: ", tool_calls)

    messages.append(response_message)

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        function_response = available_functions[function_name](
            function_args.get("timezone"),
        )
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    print(response.choices[0].message.content)


run()
