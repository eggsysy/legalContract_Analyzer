import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load your API key
load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("Here are the models your API key is allowed to use:")
print("-" * 50)

# Fetch and print the available models
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
        
print("-" * 50)