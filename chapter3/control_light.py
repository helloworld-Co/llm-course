import asyncio
import json
import os
from kasa import Discover, SmartPlug
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


# devices = asyncio.run(Discover.discover())
# for ip_address, info in devices.items():
#     print(f"{ip_address} >> {info}")


def turn_light(op: str):
    plug = SmartPlug("192.168.68.55")
    if op == "on":
        asyncio.run(plug.turn_on())
    if op == "off":
        asyncio.run(plug.turn_off())


available_functions = {
    "turn_light": turn_light,
}


def run():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "turn_light",
                "description": "Turn the light on or off.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "op": {
                            "type": "string",
                            "description": "on or off",
                        },
                    },
                    "required": ["op"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "Turn the light on",
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
        available_functions[function_name](
            **function_args,
        )


run()
