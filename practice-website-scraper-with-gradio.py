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

llama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# -----------------------------------------------------------------------------

class Website:
    url: str
    title: str
    text: str

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
# -----------------------------------------------------------------------------

system_message = "You are an assistant that analyzes the contents of a company website landing page \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown."

# ... existing code ...

def stream_brochure(company_name, url, model):
    prompt_joke = f"Please generate a jokey company brochure for {company_name}. Here is their landing page:\n"
    prompt_joke += Website(url).get_contents()
    
    if model=="Claude":
        full_text = ""
        for chunk in call_claude(prompt_joke, stream=True):
            full_text += chunk
            yield full_text
    elif model=="Llama":
        full_text = ""
        for chunk in call_llama(prompt_joke, stream=True):
            full_text += chunk
            yield full_text
    else:
        raise ValueError("Unknown model")
# ... existing code ...

# -----------------------------------------------------------------------------

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
    claude = anthropic.Anthropic(api_key=anthropic_api_key)
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

# -----------------------------------------------------------------------------

view = gr.Interface(
    fn=stream_brochure,
    inputs=[
        gr.Textbox(label="Company name:"),
        gr.Textbox(label="Landing page URL including http:// or https://"),
        gr.Dropdown(["Claude", "Llama"], label="Select model")],
    outputs=[gr.Markdown(label="Brochure:")]
)
view.launch(share=True)

