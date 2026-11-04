
from agents import run_agent
if __name__ == "__main__":
   print("===== AI LIBRARY ASSISTANT =====")
   print("Type 'exit' to stop.")
   while True:
       user_prompt = input("\nYou: ")
       if user_prompt.lower() == "exit":
           print("Assistant: Goodbye!")
           break
       if user_prompt.strip():
           run_agent(user_prompt)