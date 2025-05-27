import json


def family_health_guardian_from_gemini(ai_model, prompt_text):
    print("🔄 Sending request to Gemini API...")
    try:
        response = ai_model.generate_content(prompt_text)

        print("✅ Response received from Gemini.")

        # Debug: print raw response text
        raw_response_text = ""
        if response.parts:
            raw_response_text = response.parts[0].text
        elif hasattr(response, 'text'):
             raw_response_text = response.text
        else:
            print("🔴 ERROR: No text found in Gemini response parts.")
            return {"error": "No text content in Gemini response", "details": "Response object structure unexpected"}

        print(f"Raw Gemini response text: {raw_response_text}")

        try:
            insights_json = json.loads(raw_response_text)
            if "reply" not in insights_json:
                print(f"🔴 ERROR: 'reply' key not found in Gemini JSON response.")
                if isinstance(raw_response_text, str) and len(raw_response_text) > 10: # Arbitrary length
                     return {"reply": raw_response_text.strip()} # Return as if it was the reply
                return {"error": "'reply' key missing from JSON", "raw_response": raw_response_text}
            return insights_json 
        except json.JSONDecodeError as e:
            print(f"🔴 ERROR: Failed to decode JSON from Gemini response: {e}")
            print(f"Raw response text was: {raw_response_text}")
            if isinstance(raw_response_text, str) and len(raw_response_text) > 10: # Arbitrary length check
                 return {"reply": raw_response_text.strip()}
            return {"error": "Failed to decode JSON response", "details": str(e), "raw_response": raw_response_text}

    except Exception as e:
        print(f"🔴 ERROR: An error occurred while calling Gemini API: {e}")
        return {"error": f"Gemini API call failed: {str(e)}"}
