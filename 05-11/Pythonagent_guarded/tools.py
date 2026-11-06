import json

from pathlib import Path

from langchain.tools import tool

BASE_DIR = Path(__file__).parent

WORKSHOP_FILE = BASE_DIR / "workshops.json"

DISCOUNT_FILE = BASE_DIR / "discounts.json"


# Load workshop data

def get_workshops():
    return json.loads(

        WORKSHOP_FILE.read_text(encoding="utf-8")

    )
def cheapest():
    a=get_workshops()
    cheapest=a[0]
    for workshop in a:
        if workshop["fee"] < cheapest["fee"]:
            cheapest = workshop


    return cheapest



# Load discount data

def get_discounts():
    return json.loads(

        DISCOUNT_FILE.read_text(encoding="utf-8")

    )


# TOOL 1: List all workshops

@tool
def list_workshops() -> str:
    """Display all available workshops."""

    workshops = get_workshops()

    return json.dumps(workshops, indent=4)


# TOOL 2: Search workshops

@tool
def search_workshops(keyword: str) -> str:
    """Search workshops by title or keyword."""

    matches = [

        w for w in get_workshops()

        if keyword.lower() in w["title"].lower()

    ]

    return json.dumps(matches, indent=4)


# TOOL 3: Find workshop by ID

@tool
def find_workshop(workshop_id: str) -> str:
    """Find a workshop using its ID."""

    for workshop in get_workshops():

        if workshop["id"] == workshop_id:
            return json.dumps(workshop, indent=4)

    return "Workshop not found."


# TOOL 4: Calculate fee and apply coupon

@tool
def calculate_workshop_fee(

        workshop_id: str,

        participants: int,

        coupon_code: str = ""

) -> str:
    """Calculate workshop fee and apply a valid coupon discount."""

    if participants < 1 or participants > 30:
        return "Participants must be between 1 and 30."

    workshop = None

    for w in get_workshops():

        if w["id"] == workshop_id:
            workshop = w

            break

    if workshop is None:
        return "Workshop not found."

    original_fee = workshop["fee"] * participants

    discount_percentage = 0

    discount_amount = 0

    coupon_status = "No coupon applied."

    if coupon_code:

        coupon_code = coupon_code.strip().upper()

        for coupon in get_discounts():

            if coupon["code"].upper() == coupon_code:
                discount_percentage = coupon["discount_percentage"]

                discount_amount = (

                        original_fee * discount_percentage / 100

                )

                coupon_status = "Coupon applied successfully."

                break

        else:

            coupon_status = "Invalid coupon code."

    final_fee = original_fee - discount_amount

    result = {

        "workshop": workshop["title"],

        "participants": participants,

        "original_fee": original_fee,

        "coupon_code": coupon_code or None,

        "coupon_status": coupon_status,

        "discount_percentage": discount_percentage,

        "discount_amount": discount_amount,

        "final_fee": final_fee

    }

    return json.dumps(result, indent=4)
