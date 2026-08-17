import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY", "")
model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
print("Key present:", bool(api_key), "len:", len(api_key))
print("Model:", model)

from google import genai
from google.genai import types as genai_types

client = genai.Client(api_key=api_key)
try:
    resp = client.models.generate_content(
        model=model,
        contents="Say hello in 3 words.",
        config=genai_types.GenerateContentConfig(max_output_tokens=50, temperature=0),
    )
    print("SUCCESS:", resp.text)
except Exception as e:
    print("FAILED:", type(e).__name__, str(e))