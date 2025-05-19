# familytree/utils.py

import os
import json
import uuid
from typing import List, Optional, Literal
from pydantic import BaseModel, UUID4, HttpUrl, Field, ValidationError
from datetime import date
from enum import Enum

from kadambini.settings.base import BASE_DIR
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')


from maintree.ai_model.ai_pydentic_model import FamilyTreeData
from maintree.ai_model.ai_schema_prompt import get_schema_prompt_string


# Attempt to import google.generativeai, handle if not installed
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
except ImportError:
    print("google-generativeai library not found. Please install it using 'pip install google-generativeai'")
    exit()

try:
    # --- Configure Gemini Client ---
    api_key = ''
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
        
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        "gemini-2.0-flash", 
        generation_config=GenerationConfig(response_mime_type="application/json"),
        safety_settings={ # Added basic safety settings
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    )

except ImportError:
    print("google-generativeai library not found. Please install it using 'pip install google-generativeai'")
    genai = None
    model = None

# --- Function to generate and process family tree data ---
def generate_family_tree_data(prompt_text: str) -> FamilyTreeData:
    """
    Generates family tree data JSON from natural language instructions using Gemini.

    Args:
        prompt_text: The natural language description of the family tree.

    Returns:
        A validated FamilyTreeData Pydantic model instance.

    Raises:
        ValueError: If the Gemini model is not configured or available.
        json.JSONDecodeError: If the model response is not valid JSON.
        ValidationError: If the JSON response does not conform to the Pydantic schema.
        Exception: For other API or processing errors.
    """
    if model is None:
         raise ValueError("Gemini model is not configured. Check API key and model availability.")

    schema_description = get_schema_prompt_string()
    prompt = f"""
    {schema_description}

    Based on the following instructions, extract the information and generate a single JSON object strictly conforming to the schema described above.
    Pay special attention to the "id" field generation rules and field names (e.g., "appliesToField") as mentioned in the schema description.

    Instructions:
    {prompt_text}
    """

    try:
        response = model.generate_content(prompt)
        raw_json_text = response.text

        # Attempt to load the raw text as JSON
        llm_data = json.loads(raw_json_text)

        member_id_map = {}

        # Process members and their nested objects
        for member_data in llm_data.get("members", []):
            llm_member_id = member_data.get("id")

            if llm_member_id:
                new_member_uuid = str(uuid.uuid4())
                member_id_map[llm_member_id] = new_member_uuid
                member_data["id"] = new_member_uuid 
            else:
                 print(f"Warning: Member data missing 'id' field as temporary placeholder: {member_data}")
                 member_data["id"] = str(uuid.uuid4()) # Assign a new UUID directly

            for sub_list_key in ["conditions", "allergies", "medications", "vitals", "customTimelineEvents", "sources"]:
                for item in member_data.get(sub_list_key, []):
                    if "id" in item:
                        del item["id"]
                    if sub_list_key == "sources" and "field" in item and "appliesToField" not in item:
                         item["appliesToField"] = item.pop("field")


        # Process relationships
        for rel_data in llm_data.get("relationships", []):
            if "id" in rel_data:
                del rel_data["id"]

            llm_from_id = rel_data.get("from")
            if llm_from_id and llm_from_id in member_id_map:
                rel_data["from"] = member_id_map[llm_from_id]
            else:
                 print(f"Warning: Relationship 'from' ID '{llm_from_id}' not found in member ID map. Relationship data: {rel_data}")


            llm_to_id = rel_data.get("to")
            if llm_to_id and llm_to_id in member_id_map:
                rel_data["to"] = member_id_map[llm_to_id]
            else:
                print(f"Warning: Relationship 'to' ID '{llm_to_id}' not found in member ID map. Relationship data: {rel_data}")

        parsed_tree = FamilyTreeData.model_validate(llm_data)

        return parsed_tree 

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw text from model: {raw_json_text}")

    except ValidationError as e:
        print(f"Pydantic Validation Error: {e.json()}")
        raise 

    except Exception as e:
        print(f"An error occurred during Gemini API call or processing: {e}")
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        if 'response' in locals() and hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                 if candidate.finish_reason != 1: 
                      print(f"Candidate Finish Reason: {candidate.finish_reason}")
                      print(f"Candidate Safety Ratings: {candidate.safety_ratings}")
        raise 