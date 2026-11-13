import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
# Load .env from the project directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
# Read configuration
BASE_URL = os.getenv("FOUNDRY_CHAT_BASE_URL")
MODEL = os.getenv("FOUNDRY_MODEL")
print("Checking Azure configuration...")
print("Endpoint loaded:", bool(BASE_URL))
print("Model loaded:", MODEL)
if not BASE_URL or not MODEL:
   raise ValueError("Azure configuration missing in .env")
API_KEY = os.getenv("FOUNDRY_API_KEY")

if not API_KEY:
    raise ValueError("Azure API key missing in .env")

client = OpenAIChatCompletionClient(

    base_url=BASE_URL,

    model=MODEL,

    api_key=API_KEY

)



# ==========================================
# AGENT 1: ELIGIBILITY AGENT
# ==========================================
eligibility_agent = Agent(
   client=client,
   name="EligibilityAgent",
   instructions="""
   You are an E-commerce Return Eligibility Specialist.
   Analyze customer return requests.
   Check:
   1. Product amount.
   2. Days since delivery.
   3. Invoice availability.
   4. Item condition.
   5. Return reason.
   6. Previous returns.
   Identify eligibility issues and exceptions.
   Explain your findings clearly.
   Do not make the final approval decision.
   """
)

# ==========================================
# AGENT 2: RISK AGENT
# ==========================================
risk_agent = Agent(
   client=client,
   name="RiskAgent",
   instructions="""
   You are an E-commerce Fraud and Risk Analyst.
Analyze customer return requests.
Check:
1. Unusually frequent returns.
2. High-value requests.
3. Missing invoice evidence.
4. Missing photo evidence where relevant.
5. Suspicious return patterns.
Classify risk as LOW, MEDIUM, or HIGH.
Your response MUST contain this exact format:
RISK_LEVEL: LOW
Reasons:
- Explain the risk assessment.
Replace LOW with MEDIUM or HIGH when appropriate.
Do not make the final approval decision.
   """
)

# ==========================================
# AGENT 3: CUSTOMER RESPONSE AGENT
# ==========================================
customer_response_agent = Agent(
   client=client,
   name="CustomerResponseAgent",
   instructions="""
   You are a professional E-commerce Customer
   Support Representative.
   Generate a customer-facing response based
   on the final workflow decision.
   Explain:
   1. Approval or rejection.
   2. Whether human review was required.
   3. The reason for the decision.
   4. Next steps for the customer.
   Be polite and professional.
   Never claim that a refund has already been
   processed or a replacement has been shipped.
   This is a simulation.
   """
)

# ==========================================
# TEST ELIGIBILITY AGENT
# ==========================================
async def test_agents():
    sample_request = """

    Request ID: RET201

    Product: Wireless Keyboard

    Amount: Rs.1499

    Days since delivery: 6

    Item condition: UNOPENED

    Invoice available: True

    Photo evidence: False

    Previous returns: 0

    """

    # Test Eligibility Agent

    print("\n===== ELIGIBILITY AGENT =====")

    result1 = await eligibility_agent.run(sample_request)

    print(result1)

    # Test Risk Agent

    print("\n===== RISK AGENT =====")

    result2 = await risk_agent.run(sample_request)

    print(result2)

    # Test Customer Response Agent

    print("\n===== CUSTOMER RESPONSE AGENT =====")

    result3 = await customer_response_agent.run(

        """

        Request ID: RET201

        Final decision: AUTO_APPROVED

        Approval route: Automatic

        Reason: All business rules satisfied.

        Generate a customer communication draft.

        """

    )

    print(result3)


if __name__ == "__main__":
    asyncio.run(test_agents())
