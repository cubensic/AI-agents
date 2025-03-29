import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)




class calendar_event(BaseModel):
    name: str
    date: str
    participants: list[str]


completion = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "extract the event information"},
        {"role": "user", "content": "Alice and Bob are going to the fair on Friday"},
    ],
    response_format=calendar_event,
)
response = completion.choices[0].message.parsed
print(response)