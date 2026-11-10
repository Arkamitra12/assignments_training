import re

# STEP 1: Detect PII in user input
def contains_pii(text):
   email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
   phone_pattern = r'(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)'
   if re.search(email_pattern, text):
       return True
   if re.search(phone_pattern, text):
       return True
   return False

# STEP 2: Clean AI output
def clean_output(text):
   email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
   phone_pattern = r'(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)'
   text = re.sub(email_pattern, "[EMAIL REDACTED]", text)
   text = re.sub(phone_pattern, "[PHONE REDACTED]", text)
   return text

# STEP 3: Validate guest count
def validate_guest_count(guests):
   if guests < 1 or guests > 20:
       return False
   return True

# STEP 4: Domain restriction
def is_restaurant_question(question):
   keywords = [
       "restaurant",
       "food",
       "cuisine",
       "dining",
       "dinner",
       "lunch",
       "breakfast",
       "price",
       "cost",
       "guest",
       "people",
       "seat",
       "indian",
       "italian",
       "chinese",
       "booking",
       "reservation",
       "menu",
       "spice garden"
   ]
   question = question.lower()
   return any(word in question for word in keywords)