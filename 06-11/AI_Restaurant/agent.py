import os

from dotenv import load_dotenv

from langchain.agents import create_agent

from langchain_groq import ChatGroq

from langchain_core.messages import AIMessage, ToolMessage

from langgraph.checkpoint.memory import InMemorySaver

from guardrails import contains_pii, clean_output

from tools import (

    search_restaurants,

    calculate_dining_cost

)

# STEP 1: Load environment variables

load_dotenv()

# STEP 2: Create Groq model

model = ChatGroq(

    model=os.getenv(

        "GROQ_MODEL",
                    ),

    temperature=0

)

# STEP 3: Create conversation memory

memory = InMemorySaver()

# STEP 4: Create AI agent

agent = create_agent(

    model=model,

    tools=[

        search_restaurants,

        calculate_dining_cost

    ],

    system_prompt="""

    You are a helpful AI Restaurant Reservation Assistant.

    Your responsibilities:

    1. Help users search for restaurants.

    2. Recommend restaurants based on cuisine.

    3. Calculate estimated dining costs.

    4. Remember previously selected restaurants.

    5. Remember the previous number of guests.

    6. Handle follow-up questions using conversation history.

    IMPORTANT RULES:

    - Use the provided Python tools for restaurant information.

    - Never invent restaurant names or prices.

    - Never invent available seats.

    - Use calculate_dining_cost for cost calculations.

    - Guest count must be between 1 and 20.

    - If the user asks an unrelated question, politely

      explain that you only handle restaurant-related queries.

    - Do not implement actual bookings or payments.

    """,

    checkpointer=memory

)

# STEP 5: Run application

if __name__ == "__main__":

    thread_number = 1

    previous_count = 0

    print("\n===================================")

    print(" AI RESTAURANT RESERVATION ASSISTANT")

    print("===================================")

    print("Type /new for a new conversation")

    print("Type exit to quit")

    while True:

        question = input("\nYou: ").strip()

        # PII GUARDRAIL

        if contains_pii(question):
            print(

                "Guardrail: Personal information detected. "

                "Please remove email addresses or phone numbers."

            )

            continue

        if question.lower() == "exit":
            print("Goodbye!")

            break

        if question.lower() == "/new":
            thread_number += 1

            previous_count = 0

            print("New conversation started.")

            continue

        if not question:
            continue

        config = {

            "configurable": {

                "thread_id": f"restaurant-{thread_number}"

            }

        }

        try:

            result = agent.invoke(

                {

                    "messages": [

                        {

                            "role": "user",

                            "content": question

                        }

                    ]

                },

                config=config

            )

            messages = result["messages"]

            new_messages = messages[previous_count:]

            previous_count = len(messages)

            final_response = ""

            # DISPLAY TOOL EXECUTION

            for message in new_messages:

                if isinstance(message, AIMessage):

                    for call in message.tool_calls:
                        print("\n[TOOL SELECTED]:", call["name"])

                        print(

                            "[TOOL ARGUMENTS]:",

                            call["args"]

                        )

                    if not message.tool_calls:
                        final_response = message.content

                elif isinstance(message, ToolMessage):

                    print("\n[TOOL RESULT]:")

                    print(message.content)

            # DISPLAY FINAL RESPONSE

            if final_response:
                print("\nAgent:")

                print(clean_output(final_response))

        except Exception as error:

            print("\nError:", error)
