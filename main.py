import os
import google.generativeai as genai

GEMINI_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_KEY)

print("--- בודק מודלים זמינים למפתח שלך ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"מודל זמין: {m.name}")
except Exception as e:
    print(f"שגיאה בסריקה: {e}")
