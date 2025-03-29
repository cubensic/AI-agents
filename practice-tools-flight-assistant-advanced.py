import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

openai = OpenAI()
MODEL = "gpt-4o-mini"

system_message = (
    "You are a helpful assistant for an Airline called FlightAI.\n\n"
    "When the user wants to book a flight, follow these steps:\n"
    "1. Ask for the source city.\n"
    "2. Ask for the destination city (must be different from source).\n"
    "3. Call the function 'check_flight_availability' with the user's destination.\n"
    "   - If it returns an empty list, say: 'No flights to that city'.\n"
    "   - If it returns flights, list them EXACTLY, in a numbered list, showing airline, time, price, and duration.\n"
    "4. Wait for the user to pick one flight option by number.\n"
    "5. Then ask for passenger first name, last name, and age.\n"
    "6. Finally call 'book_flight' to confirm and show the user the real seat number and booking details.\n\n"
    "You also have a tool 'generate_report' which summarizes ALL booked tickets in a single file.\n\n"
    "IMPORTANT:\n"
    "- Always call 'check_flight_availability' if user mentions a new destination.\n"
    "- Do not invent flights or seat numbers. Use what the function calls return.\n"
    "- Source and destination cannot be the same.\n"
    "- Every time a flight is booked, produce a new ticket file named firstName_lastName_bookingNumber.txt.\n"
    "- If a city is not in flight_availability, say 'No flights found for that city'.\n"
    "If the user wants all tickets summarized, call 'generate_report' with no arguments (the function has none).\n"
    "If you don't know something, say so.\n"
    "Keep answers short and courteous.\n"
)
# ----------------------------------------------------------------------------------------------------------

# creating a tool

flight_availability = {
    "london": [
        {
            "airline": "AirlinesAI",
            "time": "10:00 AM",
            "price": "$799",
            "duration": "8 hours"
        },
        {
            "airline": "IndianAirlinesAI",
            "time": "3:00 PM",
            "price": "$899",
            "duration": "8 hours"
        },
        {
            "airline": "AmericanAirlinesAI",
            "time": "8:00 PM",
            "price": "$999",
            "duration": "8 hours"
        },
    ],
    "paris": [
        {
            "airline": "EuropeanAirlinesAI",
            "time": "11:00 AM",
            "price": "$399",
            "duration": "7 hours"
        },
        {
            "airline": "BudgetAirlines",
            "time": "6:00 PM",
            "price": "$2399",
            "duration": "7 hours"
        },
    ],
    "tokyo": [
        {
            "airline": "TokyoAirlinesAI",
            "time": "12:00 PM",
            "price": "$4000",
            "duration": "5 hours"
        },
        {
            "airline": "FastFly",
            "time": "7:00 PM",
            "price": "$1400",
            "duration": "5 hours"
        },
    ],
    "berlin": [
        {
            "airline": "BerlinAirlinesAI",
            "time": "9:00 AM",
            "price": "$499",
            "duration": "6 hours"
        },
        {
            "airline": "AmericanAirlinesAI",
            "time": "4:00 PM",
            "price": "$899",
            "duration": "6 hours"
        },
    ],
    "nagpur": [
        {
            "airline": "IndianAirlinesAI",
            "time": "8:00 AM",
            "price": "$1000",
            "duration": "10 hours"
        },
        {
            "airline": "JetAirlines",
            "time": "2:00 PM",
            "price": "$1500",
            "duration": "10 hours"
        },
        {
            "airline": "AirlinesAI",
            "time": "10:00 PM",
            "price": "$800",
            "duration": "10 hours"
        },
    ],
}

# ----------------------------------------------------------------------------------------------------------

flight_bookings = []

# ----------------------------------------------------------------------------------------------------------

def generate_ticket_numbers(seed_value):
    random.seed(seed_value)
    return [
        f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1, 99):02}"
        for _ in range(3)
    ]

# ----------------------------------------------------------------------------------------------------------

def check_flight_availability(destination_city: str):
    """
    Return the flights available for a destination city.
    If city not in flight_availability, return an empty list.
    """
    print(f"[tool] checking flight availability for {destination_city}")
    city = destination_city.lower()
    return flight_availability.get(city, [])

# ----------------------------------------------------------------------------------------------------------

def generate_ticket_file(booking_dict, booking_number):
    """
    Create a text file: firstname_lastname_bookingnumber.txt
    containing flight details
    """
    fname = booking_dict["first_name"].replace(" ", "_")
    lname = booking_dict["last_name"].replace(" ", "_")
    filename = f"{fname}_{lname}_{booking_number}.txt"

    content = (
        "Flight Ticket\n"
        "=============\n"
        f"Booking #   : {booking_number}\n"
        f"Passenger   : {booking_dict['first_name']} {booking_dict['last_name']}, Age {booking_dict['age']}\n"
        f"Source      : {booking_dict['source']}\n"
        f"Destination : {booking_dict['destination']}\n"
        f"Airline     : {booking_dict['airline']}\n"
        f"Departure   : {booking_dict['time']}\n"
        f"Price       : {booking_dict['price']}\n"
        f"Duration    : {booking_dict['duration']}\n"
        f"Seat Number : {booking_dict['seat']}\n"
    )
    with open(filename, "w") as f:
        f.write(content)

    print(f"[TOOL] Ticket file generated => {filename}")
    return filename

# ----------------------------------------------------------------------------------------------------------

def book_flight(source, destination, option_index, first_name, last_name, age):
    """
    Book a flight based on the user's choice
    - source != destination
    - index is 1-based => we do pick = idk - 1
    - create new booking record, seat assignment & ticket file
    """
    print(f"[tool] booking flight from {source} to {destination}, option {option_index}")

    if source.lower() == destination.lower():
        return "Source and destination cannot be the same"
    
    # Convert option_index from string to int

    try:
        idx = int(option_index)
    except ValueError:
        return "Invalid option index"
    
    flights = check_flight_availability(destination)
    if not flights:
        return f"Error: No flights found for {destination.title()}"
    
    chosen_flight = flights[pick]
    airline = chosen_flight["airline"]
    time = chosen_flight["time"]
    price = chosen_flight["price"]
    duration = chosen_flight["duration"]

    # Generate seat
    seat_list = generate_seat_numbers(hash(destination + airline + str(len(flight_bookings))))
    chosen_seat = seat_list[0]

    new_booking = {
        "source":      source.title(),
        "destination": destination.title(),
        "airline":     airline,
        "time":        dep_time,
        "price":       price,
        "duration":    duration,
        "seat":        chosen_seat,
        "first_name":  first_name.title(),
        "last_name":   last_name.title(),
        "age":         age,
    }
    flight_bookings.append(new_booking)

    booking_number  = len(flight_bookings)
    ticket_filename = generate_ticket_file(new_booking, booking_number)

    confirmation = (
        f"Booking #{booking_number} confirmed for {first_name.title()} {last_name.title()}. "
        f"Flight from {source.title()} to {destination.title()} on {airline} at {dep_time}. "
        f"Ticket saved to {ticket_filename}."
    )
    print(f"[TOOL] {confirmation}")
    return confirmation

# ----------------------------------------------------------------------------------------------------------

def generate_report():
    """
    Summarize ALL tickets in a single file called summary_report.txt.
    """
    print(f"[TOOL] generate_report called.")

    report_content = "Flight Booking Summary Report\n"
    report_content += "=============================\n"

    if not flight_bookings:
        report_content += "No bookings found.\n"
    else:
        for i, booking in enumerate(flight_bookings, start=1):
            report_content += (
                f"Booking #   : {i}\n"
                f"Passenger   : {booking['first_name']} {booking['last_name']}, Age {booking['age']}\n"
                f"Source      : {booking['source']}\n"
                f"Destination : {booking['destination']}\n"
                f"Airline     : {booking['airline']}\n"
                f"Departure   : {booking['time']}\n"
                f"Price       : {booking['price']}\n"
                f"Duration    : {booking['duration']}\n"
                f"Seat Number : {booking['seat']}\n"
                "-------------------------\n"
            )

    filename = "summary_report.txt"
    with open(filename, "w") as f:
        f.write(report_content)

    msg = f"Summary report generated => {filename}"
    print(f"[TOOL] {msg}")
    return msg

# ----------------------------------------------------------------------------------------------------------

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket for the city from the flight list data (not strictly needed now).",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "City name.",
            },
        },
        "required": ["destination_city"],
    },
}

availability_function = {
    "name": "check_flight_availability",
    "description": (
        "Check flight availability for the specified city. "
        "Returns a list of {airline, time, price, duration}."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "City name to check in flight_availability dict.",
            },
        },
        "required": ["destination_city"],
    },
}

book_function = {
    "name": "book_flight",
    "description": (
        "Book a flight using an option index for the chosen city. "
        "Generates a unique ticket file firstName_lastName_{bookingNumber}.txt each time."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "User's source city (must differ from destination).",
            },
            "destination": {
                "type": "string",
                "description": "User's destination city.",
            },
            "option_index": {
                "type": "string",
                "description": "1-based flight option number the user selected from check_flight_availability.",
            },
            "first_name": {
                "type": "string",
                "description": "Passenger's first name.",
            },
            "last_name": {
                "type": "string",
                "description": "Passenger's last name.",
            },
            "age": {
                "type": "string",
                "description": "Passenger's age.",
            },
        },
        "required": ["source", "destination", "option_index", "first_name", "last_name", "age"],
    },
}

report_function = {
    "name": "generate_report",
    "description": (
        "Generates a summary report of ALL tickets in summary_report.txt."
    ),
    "parameters": {
        "type": "object",
        "properties": {
        },
        "required": [],
    },
}

tools = [
    {"type": "function", "function": price_function},
    {"type": "function", "function": availability_function},
    {"type": "function", "function": book_function},
    {"type": "function", "function": report_function},
]

# ----------------------------------------------------------------------------------------------------------

def handle_tool_call(message):
    """
    The LLM can request to call a function in 'tools'. We parse the JSON arguments
    and run the Python function. Then we return a 'tool' message with the result.
    """
    tool_call = message.tool_calls[0]
    fn_name   = tool_call.function.name
    args      = json.loads(tool_call.function.arguments)

    if fn_name == "get_ticket_price":
        city = args.get("destination_city")
        flights = check_flight_availability(city)
        # In this code, we do not strictly store a single 'price' per city,
        # but let's just return the flights with price or "No flights".
        if not flights:
            response_content = {"destination_city": city, "price": "No flights found."}
        else:
            # Return the first flight's price or something
            response_content = {
                "destination_city": city,
                "price": flights[0]["price"]
            }

    elif fn_name == "check_flight_availability":
        city = args.get("destination_city")
        flights = check_flight_availability(city)
        response_content = {"destination_city": city, "availability": flights}

    elif fn_name == "book_flight":
        src        = args.get("source")
        dest       = args.get("destination")
        idx        = args.get("option_index")
        first_name = args.get("first_name")
        last_name  = args.get("last_name")
        age        = args.get("age")

        confirmation = book_flight(src, dest, idx, first_name, last_name, age)
        response_content = {
            "source": src,
            "destination": dest,
            "option_index": idx,
            "first_name": first_name,
            "last_name":  last_name,
            "age":        age,
            "confirmation": confirmation
        }

    elif fn_name == "generate_report":
        # No args needed
        msg = generate_report()
        response_content = {"report": msg}

    else:
        response_content = {"error": f"Unknown tool: {fn_name}"}

    return {
        "role": "tool",
        "content": json.dumps(response_content),
        "tool_call_id": tool_call.id,
    }, args

# ----------------------------------------------------------------------------------------------------------

def chat(message, history):
    """
    The main chat loop that handles the conversation with the user,
    passing 'tools' definitions to the LLM for function calling.
    """
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )

        # If the LLM requests a function call, handle it
        while response.choices[0].finish_reason == "tool_calls":
            msg = response.choices[0].message
            print(f"[INFO] Tool call requested: {msg.tool_calls[0]}")
            tool_response, tool_args = handle_tool_call(msg)
            print(f"[INFO] Tool response: {tool_response}")

            # Add both the LLM's request and our tool response to the conversation
            messages.append(msg)
            messages.append(tool_response)

            # Re-send updated conversation to get final or next step
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages
            )

        # Return normal text response (finish_reason = "stop")
        return response.choices[0].message.content

    except Exception as e:
        print(f"[ERROR] {e}")
        return "I'm sorry, something went wrong while processing your request."
    
# ----------------------------------------------------------------------------------------------------------

gr.ChatInterface(fn=chat, type="messages").launch()
