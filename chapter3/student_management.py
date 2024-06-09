import requests
import os
from openai import OpenAI
import json
from typing import Optional, Tuple, List


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


students = {
    0: (0, "Haotian Li", 1),
    1: (1, "Hongjun Zhang", 2),
    2: (2, "Tony Cui", 3),
    3: (3, "Xi Xiao", 3),
    4: (4, "Diana Du", 4),
    5: (5, "Ge Ji", 4),
    6: (6, "Long A", 5),
}


def get_student(student_id: int) -> Optional[Tuple[int, str, int]]:
    return students.get(student_id)


def get_all_students() -> List[Tuple[int, str, int]]:
    return list(students.values())


def get_score(student_id: int) -> Optional[int]:
    scores = {
        0: 100,
        1: 79,
        2: 75,
        3: 77,
        4: 80,
        5: 85,
        6: 76,
    }
    return scores.get(student_id)


available_functions = {
    "get_all_students": get_all_students,
    "get_student": get_student,
    "get_score": get_score
}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_student",
            "description": "Get student information by ID. If ID not found, return None. Otherwise, the return "
                           "format is tuple(student_id, name, class_id)",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "number",
                        "description": "Student ID.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_students",
            "description": "Get all students information by ID. The return "
                           "format is list of tuple(student_id, name, class_id)",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_score",
            "description": "Get score based on student ID, if not found, return None",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "number",
                        "description": "Student ID, ie. 0, 1, 2, ...",
                    },
                },
                "required": ["student_id"],
            },
        },
    }
]


def run_chat(messages, tools):
    while True:
        print("messages: ", messages)
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=1,
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        messages.append(response_message)

        print("tool_calls: ", tool_calls)

        if not tool_calls:
            break

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_response = available_functions[function_name](
                **function_args,
            )

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
                }
            )

    print(response.choices[0].message.content)


run_chat([
    {
        "role": "system",
        "content": "When getting scores of multiple students, use function get_score simultaneously way as possible.",
    },
    {
        "role": "user",
        "content": "Who is the top score student among all students?",
    },
], tools)
