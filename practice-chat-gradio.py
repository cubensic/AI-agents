import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

openai = OpenAI(api_key=openai_api_key)

llama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# -----------------------------------------------------------------------------

system_message = "You are a helpful assistant in a hair growth laser device company. \
    the company is called 'Growth Laser'. \
    encourage the customer to buy a product called '"'growth laser'"'."
    
# [{role: "user", "content": "Hello, how are you?"},
#  {role: "assistant", "content": "I'm doing well, thank you!"},
#  {role: "assistant", "content": "The capital of France is Paris."}]

# for this structure above, openAI turns this into tokens, and adds specific tokens at the beginning and end of the message, 
# so that the model can understand the message structure.
# and example would look like: <|start_of_turn|>user<|end_of_turn|>
# now, how does openai know how to differentiate between the user and assistant messages?
# it's because that's how it's been trained. 

# a way of using quotes in string is 

def chat(message, history):
    messages = [{"role": "system", "content": system_message}]
    for user_message, assistant_message in history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": assistant_message})
    messages.append({"role": "user", "content": message})

    nono_statements = ["indiana jones", "teletubbies", "price", "cost", "expensive", "budget"]

    if any(statement in message.lower() for statement in nono_statements):
        messages.append({"role": "assistant", "content": "I'm sorry, I can't answer that question."})
        yield "I'm sorry, I can't answer that question."
        return
    
# the if function above gives you a bit of control over the conversation. 
# non_statements is a list of statements that you don't want the model to answer.

    print("history is: ", history)
    print("message is: ", messages)

    stream = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ""
        yield response

gr.ChatInterface(fn=chat).launch()

