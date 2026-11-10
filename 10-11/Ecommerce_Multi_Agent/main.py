
import asyncio

from agent_framework.orchestrations import SequentialBuilder

from agents import (
    inventory_agent,
    pricing_agent,
    recommendation_agent
)


# ==========================================
# TASK 5: SEQUENTIAL ORCHESTRATION
# ==========================================

workflow = SequentialBuilder(
    participants=[
        inventory_agent,
        pricing_agent,
        recommendation_agent
    ],
    output_from="all"
).build()


# ==========================================
# RUN SHOPPING ASSISTANT
# ==========================================

async def run_shopping_assistant():

    print("\n========================================")
    print("       E-COMMERCE AI SHOPPING ASSISTANT")
    print("========================================")

    print("\nModel: GPT-OSS-20B")
    print("Provider: Groq")

    print("\nThree AI Agents are ready!")
    print("1. Inventory Agent")
    print("2. Pricing Agent")
    print("3. Recommendation Agent")

    print("\nType 'exit' to stop.")

    while True:

        user_request = input("\nCustomer: ").strip()

        if user_request.lower() in ["exit", "quit"]:
            print("\nThank you for using the Shopping Assistant!")
            break

        if not user_request:
            print("Please enter a valid request.")
            continue

        print("\nProcessing your request...")

        try:

            result = await workflow.run(user_request)

            outputs = result.get_outputs()

            print("\n========================================")
            print("              AGENT RESULTS")
            print("========================================")

            if not outputs:
                print("No response received.")
                continue

            for output in outputs:

                for message in getattr(output, "messages", []):

                    if message.role == "assistant":

                        agent_name = (
                            getattr(message, "author_name", None)
                            or "AI Agent"
                        )

                        print(f"\n--- {agent_name} ---")
                        print(message.text)

            print("\n========================================")
            print("           REQUEST COMPLETED")
            print("========================================")

        except Exception as e:

            print("\nError while processing request:")
            print("Error type:", type(e).__name__)
            print("Error details:", str(e))


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":
    asyncio.run(run_shopping_assistant())
