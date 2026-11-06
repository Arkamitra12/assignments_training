
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from guardrails import contains_pii, clean_output

from tools import (
    list_workshops,
    find_workshop,
    search_workshops,
    calculate_workshop_fee,
    cheapest
)


# STEP 1: Load environment
load_dotenv()


# STEP 2: Create GPT-4o-mini model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# STEP 3: Create agent
agent = create_agent(
    model=model,

    tools=[
        list_workshops,
        find_workshop,
        search_workshops,
        calculate_workshop_fee
    ],

    system_prompt="""
    You are a helpful Workshop Assistant.

    You can perform the following tasks:

    1. List all available workshops.
    2. Find a workshop using its ID.
    3. Search workshops by title or keyword.
    4. Calculate workshop fees.
    5. Apply coupon codes and calculate discounts.

    COUPON RULES:

    - If the user provides a coupon code,
      pass that code to calculate_workshop_fee.
    - If the user does not provide a coupon,
      calculate the original fee without a discount.
    - Always show the original fee.
    - Show the discount percentage and discount amount.
    - Show the final payable amount.
    - If a coupon is invalid, clearly inform the user.
    - Never invent coupon codes or discount percentages.

    Always use the appropriate tool to retrieve information.

    Never invent workshop names, IDs, or fees.

    Give clear and friendly answers.
    """,

    checkpointer=InMemorySaver()
)


# STEP 4: Run application
if __name__ == "__main__":

    thread_number = 1
    previous_count = 0

    print("LangChain Workshop AI Agent - GPT-4o-mini")
    print("Type /new for a new conversation")
    print("Type exit to quit")

    while True:

        question = input("\nYou: ").strip()

        if not question:
            continue

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if question.lower() == "/new":
            thread_number += 1
            previous_count = 0
            print("New conversation started.")
            continue

        if contains_pii(question):
            print("PII detected. Please remove personal contact details.")
            continue

        config = {
            "configurable": {
                "thread_id": f"workshop-{thread_number}"
            }
        }

        try:

            result = agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": question}
                    ]
                },
                config=config
            )

            messages = result["messages"]

            new_messages = messages[previous_count:]
            previous_count = len(messages)

            for msg in new_messages:

                if isinstance(msg, AIMessage):

                    for call in msg.tool_calls:
                        print("\n[TOOL]:", call["name"])
                        print("Arguments:", call["args"])

                elif isinstance(msg, ToolMessage):

                    print("\n[TOOL RESULT]:", msg.content)

            final_message = messages[-1]

            print(
                "\nAgent:",
                clean_output(final_message.content)
            )

        except Exception as error:

            print("Error:", error)
