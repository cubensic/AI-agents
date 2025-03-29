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
You are a helpful assistant that can answer questions and help with tasks. Always respond in markdown format.
"""

def call_llama(prompt, stream=False):
    messages = [{"role": "system", "content": system_message}, 
                {"role": "user", "content": prompt}]
    
    if stream:
        response = llama_via_openai.chat.completions.create(
            model="llama3.2",
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    else:
        response = llama_via_openai.chat.completions.create(
            model="llama3.2",
            messages=messages
        )
        return response.choices[0].message.content

# print(call_llama("What is the capital of France?"))

def call_claude(prompt, stream=False):
    if stream:
        response = claude.messages.create(
            model="claude-3-5-haiku-20241022",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.5,
            system=system_message,
            stream=True
        )
        for chunk in response:
            if chunk.type == "content_block_delta" and chunk.delta.text:
                yield chunk.delta.text
    else:
        response = claude.messages.create(
            model="claude-3-5-haiku-20241022",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.5,
            system=system_message
        )
        return response.content[0].text

# print(call_claude("What is the France of the capital?"))

# -----------------------------------------------------------------------------


# demo = gr.Interface(
#     fn=call_llama, 
#     inputs=[gr.Textbox(lines=2, label="Your message", placeholder="Enter your message here...")], 
#     outputs=[gr.Textbox(lines=2, label="Output", placeholder="Output...")],
#     allow_flagging=False,
#     )
# demo.launch(share=True)

# -----------------------------------------------------------------------------\

def stream_model(prompt, model):
    accumulated_text = ""
    
    if model == "llama":
        for chunk in call_llama(prompt, stream=True):
            accumulated_text += chunk
            yield accumulated_text
    elif model == "claude":
        for chunk in call_claude(prompt, stream=True):
            accumulated_text += chunk
            yield accumulated_text
    else:
        yield f"Invalid model: {model}"

view = gr.Interface(
    fn=stream_model,
    inputs=[
        gr.Textbox(lines=2, label="Your message", placeholder="Enter your message here..."), 
        gr.Radio(choices=["llama", "claude"], label="Select model", value="llama")
    ],
    outputs=gr.Markdown(label="Output"),
)
view.launch(share=True)

