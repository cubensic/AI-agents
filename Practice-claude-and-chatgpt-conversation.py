import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from IPython.display import Markdown, display, update_display

# ----------------------------------------------------------------------------------------------------------


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')


openai = OpenAI(api_key=openai_api_key)

claude = anthropic.Anthropic(api_key=anthropic_api_key)

llama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')


# ----------------------------------------------------------------------------------------------------------


if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set")


# ----------------------------------------------------------------------------------------------------------


gpt_model = "gpt-4o-mini"
claude_model = "claude-3-haiku-20240307"
llama_model = 'llama3.2'

gpt_system_prompt = "You're a piggy called Ritch. You are a master banker and notary, good with numbers. Your goal is to collaborate with others and build a thriving community."
claude_system_prompt = "You're a piggy called Pierce. You're a master smith and leatherworker. Your goal is to collaborate with others and build a thriving community."
llama_system_prompt = "You're a piggy called Hazel. You're a master farmer. Your goal is to collaborate with others and build a thriving community."

gpt_messages = [
    "Hi"
]

claude_messages = [
    "Hi"
]

llama_messages = [
    "Hi"
]

# ----------------------------------------------------------------------------------------------------------

def call_gpt():
    messages = [{"role": "system", "content": gpt_system_prompt}]
    for gpt, claude, llama in zip(gpt_messages, claude_messages, llama_messages):
        messages.append({"role": "assistant", "content": gpt})
        messages.append({"role": "user", "content": claude})
        messages.append({"role": "user", "content": llama})

    completion = openai.chat.completions.create(
        model=gpt_model,
        messages=messages
    )
    return completion.choices[0].message.content

    
# ----------------------------------------------------------------------------------------------------------

def call_claude():
    messages = []
    for gpt_msg, claude_msg, llama_msg in zip(gpt_messages, claude_messages, llama_messages):
        messages.append({"role": "user", "content": gpt_msg})
        messages.append({"role": "assistant", "content": claude_msg})
        messages.append({"role": "user", "content": llama_msg})

    messages.append({"role": "user", "content": gpt_messages[-1]})
    message = claude.messages.create(
        model=claude_model,
        system=claude_system_prompt,
        messages=messages,
        max_tokens=500
    )
    return message.content[0].text


# ----------------------------------------------------------------------------------------------------------

def call_llama():
    messages = [{"role": "system", "content": llama_system_prompt}]
    for gpt, claude, llama in zip(gpt_messages, claude_messages, llama_messages):
        messages.append({"role": "user", "content": gpt})
        messages.append({"role": "user", "content": claude})
        messages.append({"role": "assistant", "content": llama})

    # print(messages)

    try:
        response = llama_via_openai.chat.completions.create(
            model=llama_model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in Llama call: {e}")
        return "An error occurred in Llama."
    
    
# ----------------------------------------------------------------------------------------------------------

gpt_messages = ["Hi"]
claude_messages = ["Hi"]
llama_messages = ["Hi"]

print(f"GPT:\n {gpt_messages[0]}\n")
print(f"Claude:\n {claude_messages[0]}\n")
print(f"Llama:\n {llama_messages[0]}\n")

for i in range(5):
    gpt_next = call_gpt()
    print(f"GPT:\n{gpt_next}\n")
    gpt_messages.append(gpt_next)
    
    llama_next = call_llama()
    print(f"Llama:\n{llama_next}\n")
    llama_messages.append(llama_next)

    claude_next = call_claude()
    print(f"Claude:\n{claude_next}\n")
    claude_messages.append(claude_next)

