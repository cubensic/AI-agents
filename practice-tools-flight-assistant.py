import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

openai = OpenAI()
model = "gpt-4o-mini"

system_message = """
You are a helpful flight assistant specializing in providing ticket prices for various destinations.
You have access to ticket pricing information for several cities including New York, Los Angeles, Chicago, Houston, and Miami.

When a user asks about ticket prices to any of these destinations, use the get_ticket_price tool to look up the price.
If asked about destinations not in your database, or about other travel information you don't have access to, say "I don't know".

Your primary function is to help users find ticket prices for their destinations.
"""

# ----------------------------------------------------------------------------------------------------------

# creating a tool

ticket_prices = {
    "new york": 200,
    "los angeles": 300,
    "chicago": 150,
    "houston": 100,
    "miami": 250
}

def get_ticket_price(destination_city):
    print(f"Getting ticket price for {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "I don't know")

print(get_ticket_price("new york"))

# ----------------------------------------------------------------------------------------------------------

price_function = {
    "name": "get_ticket_price",
    "description": "Get the ticket price for a flight to a destination city",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The destination city"
            }
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

print(price_function)

tools = [{"type": "function", "function": price_function}]

# ----------------------------------------------------------------------------------------------------------

def chat(message, history):
    messages = [{"role": "system", "content": system_message}]
    
    # history from Gradio ChatInterface is a list of [user_msg, assistant_msg] pairs
    # we need to properly format them as OpenAI message objects
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    
    # Add the current user message
    messages.append({"role": "user", "content": message})
    
    # Make the API call - use non-streaming version for simplicity
    response = openai.chat.completions.create(
        model=model, 
        messages=messages, 
        tools=tools
    )

    # Check if the model wants to use a tool
    if response.choices[0].finish_reason == "tool_calls":
        # Process the tool call
        tool_response, city = handle_tool_call(response.choices[0].message)
        
        # Add tool response to messages
        messages.append(response.choices[0].message)
        messages.append(tool_response)
        
        # Get final response incorporating tool results
        final_response = openai.chat.completions.create(model=model, messages=messages)
        return final_response.choices[0].message.content
    
    # Return the regular response if no tool is used
    return response.choices[0].message.content


# this function above I fixed using Cursor. 
# this time, the call for open has "tools", which is a list of tools that the model can use
# gr.ChatInterface(fn=chat).launch()

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    city = arguments["destination_city"]
    price = get_ticket_price(city)
    response = {
        "role": "tool",
        "content": json.dumps({"destination_city": city, "price": price}),
        "tool_call_id": message.tool_calls[0].id
    }
    return response, city

gr.ChatInterface(
fn=chat).launch(share=True)

# ----------------------------------------------------------------------------------------------------------

def create_audio(
        text, 
        voice="alloy"
        ):
    """
    Generate audio from text using OpenAI's text-to-speech API.
    
    Args:
        text (str): The text to convert to speech
        voice (str): The voice to use (options: alloy, echo, fable, onyx, nova, shimmer)
                     Default is "alloy"
    
    Returns:
        str: Path to the saved audio file
    """
    print(f"Generating audio for: {text}")
    
    response = openai.audio.speech.create(
        model="tts-1",  # or "tts-1-hd" for higher quality
        voice=voice,
        input=text
    )
    
    # Save the audio file locally
    output_file = "flight_assistant_response.mp3"
    
    # Fix for the deprecated stream_to_file method
    with open(output_file, "wb") as file:
        for chunk in response.iter_bytes():
            file.write(chunk)
    
    return output_file

# Example usage
audio_file = create_audio("The ticket price to New York is $200. Have a great trip!")
print(f"Audio saved to: {audio_file}")

# ----------------------------------------------------------------------------------------------------------

