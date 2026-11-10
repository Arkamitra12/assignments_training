import os

import json

from dotenv import load_dotenv

from agent_framework import Agent, tool

from agent_framework.openai import OpenAIChatCompletionClient

from tools import search_products, calculate_order_total

# Load environment variables

load_dotenv()

# Get Groq API key

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env file")

# Configure GPT-OSS-20B through Groq

chat_client = OpenAIChatCompletionClient(
    model="openai/gpt-oss-20b",
                       api_key=GROQ_API_KEY,
                       base_url="https://api.groq.com/openai/v1",

                    )



# ==========================================

# PYTHON TOOL WRAPPERS

# ==========================================

@tool(approval_mode="never_require")
def product_search_tool(query: str) -> str:
    """Search products by product name or category."""

    result = search_products(query)

    return json.dumps(result, ensure_ascii=False)


@tool(approval_mode="never_require")
def order_calculation_tool(product_id: str, quantity: int) -> str:
    """Calculate order total and verify available stock."""

    result = calculate_order_total(product_id, quantity)

    return json.dumps(result, ensure_ascii=False)


# ==========================================

# AGENT 1: INVENTORY AGENT

# ==========================================

inventory_agent = Agent(

    client=chat_client,


    instructions="""

    You are an Inventory Management Agent for an e-commerce company.

    Your responsibilities:

    1. Understand the customer's product requirements.

    2. Identify the requested product category.

    3. Use product_search_tool to search the product dataset.

    4. Display matching products.

    5. Show product ID, name, price, stock and rating.

    6. Identify products with sufficient stock.

    7. Never invent product information.

    Pass the matching product information to the Pricing Agent.

    If no matching products are found, clearly report that.

    """,

    tools=[product_search_tool]

)

# ==========================================

# AGENT 2: PRICING AGENT

# ==========================================

pricing_agent = Agent(

    client=chat_client,


    instructions= """

    You are a Pricing Agent for an e-commerce company.

    Your responsibilities:

    1. Read the customer's original request.

    2. Read the product information provided by the Inventory Agent.

    3. Identify the requested quantity and total budget.

    4. Use order_calculation_tool to calculate the total cost.

    5. Verify that sufficient stock is available.

    6. Check whether the total price is within the customer's budget.

    7. Reject products that exceed the budget.

    8. Never recommend products with insufficient stock.

    Pass the valid product and pricing information

    to the Recommendation Agent.

    Never invent prices or stock information.

    """,

    tools=[order_calculation_tool]

)

# ==========================================

# AGENT 3: RECOMMENDATION AGENT

# ==========================================

recommendation_agent = Agent(

    client=chat_client,

    name="Recommendation Agent",

    instructions="""

    You are a Product Recommendation Agent.

    Your responsibilities:

    1. Review the inventory results.

    2. Review the pricing results.

    3. Consider only products that satisfy the customer's

       quantity, stock and total budget requirements.

    4. Recommend the highest-rated suitable product.

    5. If ratings are equal, prefer the lower-cost option.

    6. Never recommend unavailable products.

    7. Explain briefly why the product is recommended.

    Display:

    - Recommended product name

    - Product ID

    - Quantity

    - Unit price

    - Total cost

    - Customer rating

    - Reason for recommendation

    If no product satisfies the requirements,

    clearly inform the customer.

    """

)

print("Three AI agents created successfully!")

print("Model: openai/gpt-oss-20b")

print("Provider: Groq")
