import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is helloworld.net?",
        },
    ],
    model="gpt-3.5-turbo",
)

print(completion.choices[0].message.content)
