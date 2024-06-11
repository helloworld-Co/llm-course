import sqlite3
import os
import json
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


movies = [
    (1, "惊天魔盗团", "mystery", 115, "Universal"),
    (2, "加勒比海盗1", "action", 125, "Disney"),
    (3, "加勒比海盗2", "action", 126, "Disney"),
    (4, "加勒比海盗3", "action", 132, "Disney"),
    (5, "星球大战", "action", 111, "Universal"),
    (6, "寻梦环游记", "fantasy", 120, "Universal"),
    (7, "寂静岭", "horror", 126, "Disney"),
    (8, "十二宫杀手", "crime", 140, "Universal"),
]

create_table_sql = """
    CREATE TABLE movie (
        id INTEGER PRIMARY KEY, -- movie ID, 1, 2, 3, ...
        name TEXT NOT NULL, -- movie name
        type TEXT NOT NULL, -- movie type, ie. horror, fantasy, western, action, etc. 
        length INTEGER, -- movie length in minutes
        producer TEXT -- producer of the movie
    );
"""


con = sqlite3.connect(":memory:")


def setup():
    cur = con.cursor()
    cur.execute(create_table_sql)
    cur.executemany("INSERT INTO movie VALUES(?, ?, ?, ?, ?)", movies)
    con.commit()


def execute_sql(sql):
    cur = con.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    return json.dumps(res)


available_functions = {
    "execute_sql": execute_sql,
}


def run(question):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_sql",
                "description": "Execute SQL on cinema database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": f"SQL running on cinema database. The database has tables: {create_table_sql}",
                        },
                    },
                    "required": ["sql"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "Based on cinema DB, answer question.",
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    print("tool_calls: ", tool_calls)

    messages.append(response_message)

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
                "content": function_response,
            }
        )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )

    print(response.choices[0].message.content)


setup()
run("What are available action movies?")
run("What movies having length shorter than 120 min?")