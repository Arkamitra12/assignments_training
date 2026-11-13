# ==========================================

# TASK 3: IMPLEMENT BUSINESS RULES

# ==========================================


def evaluate_business_rules(request, risk_level):
    findings = {}

    # RULE 1: Product amount below Rs. 25,000

    findings["amount_check"] = (

            request["amount_inr"] < 25000

    )

    # RULE 2: Return within 30 days

    findings["delivery_check"] = (

            request["days_since_delivery"] <= 30

    )

    # RULE 3: Invoice must be available

    findings["invoice_check"] = (

            request["invoice_available"] is True

    )

    # RULE 4: Item must be unopened OR damaged

    # with supporting photographs

    condition = request["item_condition"].upper()

    item_condition_valid = (

            condition == "UNOPENED"

            or (

                    condition == "DAMAGED"

                    and request["photo_evidence_available"] is True

            )

    )

    findings["item_condition_check"] = item_condition_valid

    # RULE 5: Fewer than 3 previous returns

    findings["previous_returns_check"] = (

            request["previous_returns_90_days"] < 3

    )

    # RULE 6: Risk must not be HIGH

    findings["risk_check"] = (

            risk_level.strip().upper() != "HIGH"

    )

    # All conditions must be satisfied

    automatic_approval = all(findings.values())

    if automatic_approval:

        decision = "AUTO_APPROVED"

        approval_route = "Automatic"

    else:

        decision = "HUMAN_REVIEW"

        approval_route = "Human Review"

    return {

        "request_id": request["request_id"],

        "order_id": request["order_id"],

        "findings": findings,

        "risk_level": risk_level.upper(),

        "approval_route": approval_route,

        "decision": decision

    }


# ==========================================

# TEST BUSINESS RULES

# ==========================================

if __name__ == "__main__":

    import json

    with open("returns.json", "r", encoding="utf-8") as file:

        requests = json.load(file)

    # Test the first customer request

    request = requests[0]

    # Temporary test risk level.

    # Later, this will come from the Risk Agent.

    risk_level = "LOW"

    result = evaluate_business_rules(

        request,

        risk_level

    )

    print("\n========== BUSINESS RULE RESULTS ==========")

    print("Request ID:", result["request_id"])

    print("Order ID:", result["order_id"])

    print("\nIndividual Rule Results:")

    for rule, status in result["findings"].items():
        print(rule, ":", "PASS" if status else "FAIL")

    print("\nApproval Route:", result["approval_route"])

    print("Final Decision:", result["decision"])
