import google.generativeai as genai
import json

def get_hereditary_risk_insights_prompt_from_gemini(ai_model,prompt_text):
    print("🔄 Sending request to Gemini API...")
    try:
        response = ai_model.generate_content(
            prompt_text
        )
        print("✅ Response received from Gemini.")

        if response.parts:
            json_response_text = response.parts[0].text
        else: 
            json_response_text = response.text

        try:
            insights_json = json.loads(json_response_text)
            print(insights_json)
            return insights_json
        except json.JSONDecodeError as e:
            print(f"🔴 ERROR: Failed to decode JSON from Gemini response: {e}")
            print(f"Raw response text was: {json_response_text}")
            return {"error": "Failed to decode JSON response", "details": str(e), "raw_response": json_response_text}

    except Exception as e:
        print(f"🔴 ERROR: An error occurred while calling Gemini API: {e}")
        return {"error": f"Gemini API call failed: {str(e)}"}
