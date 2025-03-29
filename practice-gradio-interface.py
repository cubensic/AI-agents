import gradio as gr
import os
import requests
import anthropic
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------------------------------------------------------

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')


openai = OpenAI(api_key=openai_api_key)

claude = anthropic.Anthropic(api_key=anthropic_api_key)

llama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')


# -----------------------------------------------------------------------------

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set")

# -----------------------------------------------------------------------------

system_message = """
You are a helpful assistant that can answer questions and help with tasks.
"""

def message(prompt):
    messages = [
        {"role": "system", "content": "system_message"},
        {"role": "user", "content": prompt}
    ]
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return completion.choices[0].message.content

# print(message("What is the capital of France?"))

# -----------------------------------------------------------------------------

# def shout(message):
#     print(f"Shouting: {message}")
#     return message.upper()

# print(shout("Hello, world!"))

# demo = gr.Interface(
#     fn=shout, 
#     inputs=[gr.Textbox(lines=2, label="Your message", placeholder="Enter your message here...")], 
#     outputs=[gr.Textbox(lines=2, label="Shouted message", placeholder="Shouted message...")],
#     allow_flagging=False,
#     )

# demo.launch(share=True)

# -----------------------------------------------------------------------------

demo = gr.Interface(
    fn=message, 
    inputs=[gr.Textbox(lines=2, label="Your message", placeholder="Enter your message here...")], 
    outputs=[gr.Textbox(lines=2, label="Output", placeholder="Output...")],
    allow_flagging=False,
    )
demo.launch(share=True)

