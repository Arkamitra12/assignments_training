import asyncio

import json
with open("returns.json","r",encoding="utf-8") as file:
    returns = json.load(file)

import re

from agent_framework import (

    Executor,

    WorkflowBuilder,

    WorkflowContext,

    handler,

    response_handler

)

from agents import (

    eligibility_agent,

    risk_agent,

    customer_response_agent

)

from business_rules import evaluate_business_rules


# ==========================================

# EXECUTOR 1: ELIGIBILITY AGENT

# ==========================================

class EligibilityExecutor(Executor):

    def __init__(self):
        super().__init__(id="eligibility_executor")

    @handler
    async def process(

            self,

            request: dict,

            ctx: WorkflowContext[dict, dict]

    ):
        print("\n[1] ELIGIBILITY AGENT RUNNING...")

        prompt = f"""

        Analyze this customer return request:

        {json.dumps(request, indent=2)}

        Review the return request against the company's

        return policy.

        Identify eligibility conditions and exceptions.

        Explain your findings clearly.

        Do not make the final approval decision.

        """

        result = await eligibility_agent.run(prompt)

        output = {

            "request": request,

            "eligibility_analysis": str(result)

        }

        await ctx.send_message(output)


# ==========================================

# EXECUTOR 2: RISK AGENT

# ==========================================

class RiskExecutor(Executor):

    def __init__(self):
        super().__init__(id="risk_executor")

    @handler
    async def process(

            self,

            data: dict,

            ctx: WorkflowContext[dict, dict]

    ):
        print("\n[2] RISK AGENT RUNNING...")

        prompt = f"""

        Analyze this return request for potential risks.

        Customer Request:

        {json.dumps(data["request"], indent=2)}

        Eligibility Findings:

        {data["eligibility_analysis"]}

        Check:

        1. Unusual return frequency.

        2. Missing evidence.

        3. High-value requests.

        4. Suspicious return patterns.

        Return your assessment in EXACTLY this format:

        RISK_LEVEL: LOW / MEDIUM / HIGH

        Reasons:

        Explain your assessment.

        Do not make the final approval decision.

        """

        result = await risk_agent.run(prompt)

        risk_analysis = str(result)

        # Extract risk level

        match = re.search(

            r"RISK[_ ]LEVEL\s*:\s*(LOW|MEDIUM|HIGH)",

            risk_analysis,

            re.IGNORECASE

        )

        # Conservative fallback

        risk_level = (

            match.group(1).upper()

            if match

            else "HIGH"

        )

        output = {

            **data,

            "risk_analysis": risk_analysis,

            "risk_level": risk_level

        }

        await ctx.send_message(output)


# ==========================================

# EXECUTOR 3: APPROVAL GATEWAY

# ==========================================

class ApprovalGatewayExecutor(Executor):

    def __init__(self):

        super().__init__(id="approval_gateway")

    @handler
    async def process(

            self,

            data: dict,

            ctx: WorkflowContext[dict, dict]

    ):

        print("\n[3] APPROVAL GATEWAY RUNNING...")

        # Apply deterministic Python business rules

        decision = evaluate_business_rules(

            data["request"],

            data["risk_level"]

        )

        output = {

            **data,

            "business_rule_results": decision,

            "approval_route": decision["approval_route"],

            "final_decision": decision["decision"]

        }

        print("\nBUSINESS RULE RESULTS:")

        for rule, passed in decision["findings"].items():
            status = "PASS" if passed else "FAIL"

            print(f"{rule}: {status}")

        print("\nApproval Route:", decision["approval_route"])

        # ----------------------------------

        # AUTOMATIC APPROVAL

        # ----------------------------------

        if decision["decision"] == "AUTO_APPROVED":
            print("Decision: AUTO_APPROVED")

            await ctx.send_message(output)

            return

        # ----------------------------------

        # HUMAN APPROVAL REQUIRED

        # ----------------------------------

        print("\n!!! HUMAN APPROVAL REQUIRED !!!")

        review_details = {

            "workflow_data": output,

            "request_id": data["request"]["request_id"],

            "product": data["request"]["product"],

            "amount": data["request"]["amount_inr"],

            "eligibility_issues": [

                rule

                for rule, passed in decision["findings"].items()

                if not passed

            ],

            "risk_analysis": data["risk_analysis"],

            "risk_level": data["risk_level"]

        }

        # Pause workflow and request manager input

        await ctx.request_info(

            request_data=review_details,

            response_type=str,

            request_id=f"manager_{data['request']['request_id']}"

        )

    # ======================================

    # MANAGER RESPONSE HANDLER

    # ======================================

    @response_handler
    async def handle_manager_response(

            self,

            original_request: dict,

            response: str,

            ctx: WorkflowContext[dict, dict]

    ):

        manager_decision = response.strip().upper()

        # Defensive input validation

        if manager_decision not in ["APPROVE", "REJECT"]:
            raise ValueError(

                "Invalid manager decision. "

                "Expected APPROVE or REJECT."

            )

        output = original_request["workflow_data"].copy()

        # Human decision is final

        if manager_decision == "APPROVE":

            output["final_decision"] = "MANAGER_APPROVED"

        else:

            output["final_decision"] = "MANAGER_REJECTED"

        output["approval_route"] = "Human Review"

        output["manager_decision"] = manager_decision

        print("\nMANAGER DECISION:", manager_decision)

        print(

            "FINAL DECISION:",

            output["final_decision"]

        )

        # Continue workflow

        await ctx.send_message(output)


# ==========================================

# EXECUTOR 4: CUSTOMER RESPONSE AGENT

# ==========================================

class CustomerResponseExecutor(Executor):

    def __init__(self):
        super().__init__(id="customer_response_executor")

    @handler
    async def process(

            self,

            data: dict,

            ctx: WorkflowContext[dict, dict]

    ):
        print("\n[4] CUSTOMER RESPONSE AGENT RUNNING...")

        prompt = f"""

        Generate a professional customer communication draft.

        Request ID:

        {data["request"]["request_id"]}

        Order ID:

        {data["request"]["order_id"]}

        Product:

        {data["request"]["product"]}

        Requested Amount:

        Rs. {data["request"]["amount_inr"]}

        Eligibility Findings:

        {data["eligibility_analysis"]}

        Risk Assessment:

        {data["risk_analysis"]}

        Approval Route:

        {data["approval_route"]}

        Final Decision:

        {data["final_decision"]}

        Rules:

        1. If AUTO_APPROVED, communicate automatic approval.

        2. If MANAGER_APPROVED, communicate manager approval.

        3. If MANAGER_REJECTED, communicate rejection.

        4. Never claim that a refund has already been processed.

        5. Never invent shipping or refund timelines.

        6. If awaiting review, communicate that the request

           is pending manager approval.

        Generate only the customer communication draft.

        """

        response = await customer_response_agent.run(prompt)

        # Final structured output

        final_output = {

            "request_id": data["request"]["request_id"],

            "order_id": data["request"]["order_id"],

            "product": data["request"]["product"],

            "requested_amount": data["request"]["amount_inr"],

            "eligibility_findings": data["eligibility_analysis"],

            "risk_assessment": data["risk_analysis"],

            "risk_level": data["risk_level"],

            "business_rule_results": data["business_rule_results"],

            "approval_route": data["approval_route"],

            "final_decision": data["final_decision"],

            "manager_decision": data.get(

                "manager_decision",

                "NOT_REQUIRED"

            ),

            "customer_communication": str(response)

        }

        await ctx.yield_output(final_output)


# ==========================================

# BUILD GRAPH WORKFLOW

# ==========================================

eligibility_executor = EligibilityExecutor()

risk_executor = RiskExecutor()

approval_executor = ApprovalGatewayExecutor()

response_executor = CustomerResponseExecutor()

workflow = (

    WorkflowBuilder(

        start_executor=eligibility_executor

    )

    .add_edge(

        eligibility_executor,

        risk_executor

    )

    .add_edge(

        risk_executor,

        approval_executor

    )

    .add_edge(

        approval_executor,

        response_executor

    )

    .build()

)


# ==========================================

# HUMAN APPROVAL INPUT

# ==========================================

def get_manager_decision(details):
    print("\n")

    print("=" * 50)

    print("             MANAGER REVIEW")

    print("=" * 50)

    print("\nRequest ID:", details["request_id"])

    print("Product:", details["product"])

    print("Amount: Rs.", details["amount"])

    print(

        "\nEligibility Issues:",

        details["eligibility_issues"]

    )

    print("\nRisk Level:", details["risk_level"])

    print("\nRisk Assessment:")

    print(details["risk_analysis"])

    print("\n" + "=" * 50)

    while True:

        decision = input(

            "\nManager Decision (APPROVE / REJECT): "

        ).strip().upper()

        if decision in ["APPROVE", "REJECT"]:
            return decision

        print(

            "Invalid input! "

            "Please enter APPROVE or REJECT."

        )


# ==========================================

# RUN WORKFLOW

# ==========================================
# ==========================================

# PROCESS EACH CUSTOMER REQUEST

# ==========================================

async def process_request(request):
    print("\n" + "=" * 50)

    print("PROCESSING REQUEST:", request["request_id"])

    print("=" * 50)

    stream = workflow.run(

        request,

        stream=True

    )

    while True:

        pending_responses = {}

        final_output = None

        async for event in stream:

            # Human approval required

            if event.type == "request_info":

                details = event.data

                print("\n========== MANAGER REVIEW ==========")

                print("Request ID:", details["request_id"])

                print("Product:", details["product"])

                print("Amount:", details["amount"])

                print(

                    "Eligibility Issues:",

                    details["eligibility_issues"]

                )

                print("Risk Level:", details["risk_level"])

                print("Risk Assessment:")

                print(details["risk_analysis"])

                while True:

                    manager_decision = input(

                        "\nEnter APPROVE or REJECT: "

                    ).strip().upper()

                    if manager_decision in ["APPROVE", "REJECT"]:
                        break

                    print("Invalid input! Try again.")

                pending_responses[event.request_id] = (

                    manager_decision

                )

            # Final output received

            elif event.type == "output":

                final_output = event.data

        # Workflow completed

        if final_output is not None:
            print("\n========== FINAL RESULT ==========")

            print(

                json.dumps(

                    final_output,

                    indent=4,

                    ensure_ascii=False

                )

            )

            break

        # Resume workflow after manager decision

        if pending_responses:

            print("\nResuming workflow...")

            stream = workflow.run(

                stream=True,

                responses=pending_responses

            )

        else:

            print("Workflow ended without final output.")

            break


async def main():
    # Load all customer requests

    with open(

            "returns.json",

            "r",

            encoding="utf-8"

    ) as file:

        requests = json.load(file)

    # ----------------------------------

    # SELECT REQUEST FOR TESTING

    # ----------------------------------

    # RET202 is the second record.

    # It should require human review.

    for request in requests:
        await process_request(request)

    print("\n")

    print("=" * 50)

    print(" E-COMMERCE RETURNS AND REFUND WORKFLOW ")

    print("=" * 50)

    print("\nProcessing Request:", request["request_id"])

    # Initial workflow execution

    stream = workflow.run(

        request,

        stream=True

    )

    while True:

        pending_responses = {}

        final_output = None

        # Listen to workflow events

        async for event in stream:

            # ----------------------------------

            # HUMAN REVIEW REQUEST

            # ----------------------------------

            if event.type == "request_info":

                details = event.data

                manager_decision = get_manager_decision(

                    details

                )

                pending_responses[event.request_id] = (

                    manager_decision

                )

            # ----------------------------------

            # FINAL OUTPUT

            # ----------------------------------

            elif event.type == "output":

                final_output = event.data

        # ----------------------------------

        # WORKFLOW COMPLETED

        # ----------------------------------

        if final_output is not None:
            print("\n")

            print("=" * 50)

            print("          FINAL WORKFLOW OUTPUT")

            print("=" * 50)

            print(

                json.dumps(

                    final_output,

                    indent=4,

                    ensure_ascii=False

                )

            )

            break

        # ----------------------------------

        # RESUME PAUSED WORKFLOW

        # ----------------------------------

        if pending_responses:

            print("\nResuming workflow...")

            stream = workflow.run(

                stream=True,

                responses=pending_responses

            )

        else:

            print("\nWorkflow ended without final output.")

            break


# ==========================================

# MAIN

# ==========================================

if __name__ == "__main__":
    asyncio.run(main())
