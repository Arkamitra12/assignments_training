import os

import json

import inspect

from groq import Groq

from dotenv import load_dotenv

from tools import search_books, reserve_book

# ==========================================

# 1. LOAD GROQ API KEY

# ==========================================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env file")

client = Groq(api_key=API_KEY)

MODEL = "openai/gpt-oss-20b"

# ==========================================

# 2. DEFINE PYTHON TOOLS

# ==========================================

tools = [

    {

        "type": "function",

        "function": {

            "name": "search_books",

            "description": "Search for books using title, author or keyword.",

            "parameters": {

                "type": "object",

                "properties": {

                    "query": {

                        "type": "string",

                        "description": "Book title, author or keyword"

                    }

                },

                "required": ["query"]

            }

        }

    },

    {

        "type": "function",

        "function": {

            "name": "reserve_book",

            "description": "Reserve an available book for a customer.",

            "parameters": {

                "type": "object",

                "properties": {

                    "book_id": {

                        "type": "integer",

                        "description": "ID of the book"

                    },

                    "customer_name": {

                        "type": "string",

                        "description": "Name of the customer"

                    }

                },

                "required": ["book_id", "customer_name"]

            }

        }

    }

]


# ==========================================

# 3. EXECUTE SELECTED PYTHON TOOL

# ==========================================

def execute_tool(function_name, arguments):
    print(f"\n[Agent Decision]: Executing tool '{function_name}'")

    print("Arguments:", arguments)

    if function_name == "search_books":

        # Support either query or keyword in tools.py

        signature = inspect.signature(search_books)

        parameter_names = signature.parameters

        if "query" in parameter_names:

            result = search_books(query=arguments["query"])

        elif "keyword" in parameter_names:

            result = search_books(keyword=arguments["query"])

        else:

            result = search_books(arguments["query"])

        return result

    elif function_name == "reserve_book":

        signature = inspect.signature(reserve_book)

        parameter_names = signature.parameters

        reserve_arguments = {

            "book_id": arguments["book_id"],

            "customer_name": arguments["customer_name"]

        }

        # Support tools.py versions with a confirmation parameter

        if "confirmed" in parameter_names:
            reserve_arguments["confirmed"] = True

        result = reserve_book(**reserve_arguments)

        return result

    else:

        return {"error": "Unknown tool requested"}


# ==========================================

# 4. AI AGENT

# ==========================================

def run_agent(user_prompt):
    messages = [

        {

            "role": "system",

            "content": """

            You are an AI Library Assistant.

            Your responsibilities are:

            1. Search books.

            2. Check book availability.

            3. Reserve books for customers.

            Rules:

            - Use search_books when the user asks to find books.

            - Use reserve_book when the user wants to reserve a book.

            - Never invent book information.

            - Always check availability before reservation.

            - Never reserve a book without customer confirmation.

            - If no copies are available, inform the user.

            - Give clear and friendly responses.

            """

        },

        {

            "role": "user",

            "content": user_prompt

        }

    ]

    try:

        # ==================================

        # FIRST API CALL: AI DECIDES TOOL

        # ==================================

        response = client.chat.completions.create(

            model=MODEL,

            messages=messages,

            tools=tools,

            tool_choice="auto"

        )

        assistant_message = response.choices[0].message

        # ==================================

        # CHECK WHETHER TOOL IS SELECTED

        # ==================================

        if assistant_message.tool_calls:

            # Add assistant tool-call message

            messages.append({

                "role": "assistant",

                "content": assistant_message.content or "",

                "tool_calls": [

                    {

                        "id": tool_call.id,

                        "type": "function",

                        "function": {

                            "name": tool_call.function.name,

                            "arguments": tool_call.function.arguments

                        }

                    }

                    for tool_call in assistant_message.tool_calls

                ]

            })

            # ==================================

            # EXECUTE SELECTED TOOL

            # ==================================

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name

                arguments = json.loads(

                    tool_call.function.arguments

                )

                result = execute_tool(

                    function_name,

                    arguments

                )

                print("\n[Tool Output]:", result)

                # ==================================

                # SEND TOOL RESULT BACK TO AI

                # ==================================

                messages.append({

                    "role": "tool",

                    "tool_call_id": tool_call.id,

                    "content": json.dumps(

                        result,

                        default=str

                    )

                })

            # ==================================

            # SECOND API CALL: FINAL RESPONSE

            # ==================================

            final_response = client.chat.completions.create(

                model=MODEL,

                messages=messages

            )

            final_answer = final_response.choices[0].message.content

            print("\nAssistant:", final_answer)

            return final_answer

        else:

            final_answer = assistant_message.content

            print("\nAssistant:", final_answer)

            return final_answer

    except Exception as error:

        print("\nAgent Error:", error)

        return None


# ==========================================

# 5. RUN AGENT DIRECTLY

# ==========================================

if __name__ == "__main__":

    print("\n===== AI LIBRARY ASSISTANT =====")

    print("Type 'exit' to stop.\n")

    while True:

        user_prompt = input("\nYou: ").strip()

        if user_prompt.lower() == "exit":
            print("\nAssistant: Goodbye!")

            break

        if user_prompt:
            run_agent(user_prompt)
