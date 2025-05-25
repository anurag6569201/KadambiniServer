import os
from pydantic import ValidationError as PydanticValidationError

def ai_config():
    try:
        import google.generativeai as genai
        from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
    except ImportError:
        print("google-generativeai library not found. Please install it using 'pip install google-generativeai'")
        return None, None

    # Retrieve API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("GEMINI_API_KEY environment variable not set.")
        return None, None

    # Configure the Gemini client
    genai.configure(api_key=api_key)

    # Create and return the model
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config=GenerationConfig(response_mime_type="application/json"),
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    )

    return model
