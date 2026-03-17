
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables")

genai.configure(api_key=api_key)

print("Available models that support 'generateContent':")
for model in genai.list_models():
  if 'generateContent' in model.supported_generation_methods:
    print(f"- {model.name}")
