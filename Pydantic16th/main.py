import json
import logging
from textwrap import indent
from typing import Literal
from pathlib import Path
from pydantic import BaseModel, ValidationError, Field, TypeAdapter

logging.basicConfig(
    filename="registrations.log",
    filemode="w",
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)


# Pydantic model
class Registration(BaseModel):
    registration_id : str
    name: str
    email: str
    age: int = Field(gt=18)
    ticket_type: Literal["Standard" , "Premium" , "VIP"]
    amount: float = Field(gt=0)

logging.info("Starting registrations data validation process...")

total_records = 0
valid_records = 0
invalid_records = 0
valid_record_list = []

try:
    json_data = Path("registrations.json").read_text()
    registrations = json.loads(json_data)
    total_records = len(registrations)
    print("___Valid Registrations___")

    for registration in registrations:
        try:
            valid_registration =Registration.model_validate(registration)
            logging.info(f"Successfully validated registration: {valid_registration.registration_id}")
            print(valid_registration)
            valid_record_list.append(valid_registration.model_dump())
            valid_records += 1

        except ValidationError as e:
            reg_id = registration.get('registration_id')
            logging.warning(f"Validation Error for Registration ID:  {reg_id}")
            invalid_records += 1
            print(f"\n Validation Error for Registration ID:  {reg_id}")
            for error in e.errors():
                field_name = error["loc"][0]
                error_msg = error["msg"]
                logging.error(f"{field_name}: {error_msg}")
                print(f"{field_name}: {error_msg}")


    output_file = Path("valid_registrations.json")
    output_file.write_text(json.dumps(valid_record_list , indent=4))

except FileNotFoundError as e:
    logging.error(e)

except json.JSONDecodeError as e:
    logging.error(e)



print("\n SUMMARY")
print(f"Total records:   {total_records}")
print(f"Valid records:   {valid_records}")
print(f"Invalid records: {invalid_records}")