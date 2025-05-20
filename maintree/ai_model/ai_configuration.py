# familytree/utils.py

import os
import json
import uuid
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, UUID4, HttpUrl, Field, ValidationError as PydanticValidationError
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
    api_key = 'AIzaSyC4Tvo195jhgPu2ciymMHOMbjJsZV-MdUs'
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


# --- Function to MODIFY existing family tree data ---
def modify_family_tree_data(current_tree_dict: Dict[str, Any], modification_prompt_text: str) -> FamilyTreeData:
    """
    Modifies an existing family tree based on natural language instructions using Gemini.

    Args:
        current_tree_dict: The current family tree as a Python dictionary.
        modification_prompt_text: Natural language instructions for modification.

    Returns:
        A validated FamilyTreeData Pydantic model instance representing the modified tree.

    Raises:
        ValueError: If the Gemini model is not configured or available.
        json.JSONDecodeError: If the model response is not valid JSON.
        PydanticValidationError: If the JSON response does not conform to the Pydantic schema.
        Exception: For other API or processing errors.
    """
    if model is None:
        raise ValueError("Gemini model is not configured. Check API key and model availability.")

    schema_description = get_schema_prompt_string() # This describes the general schema structure
    current_tree_json_string = json.dumps(current_tree_dict, indent=2)

    # Construct the prompt specifically for modification
    prompt = f"""
    You will be given an existing family tree JSON object and a set of instructions to modify it.
    Your task is to return a *new, complete* JSON object that incorporates these changes, strictly conforming to the schema described below.
    Do NOT include any markdown like ```json or ```.

    Regarding "id" fields in the *modified* JSON you output:
    - For "members":
        - If you are *adding a new member*, provide a unique temporary string placeholder for its "id" (e.g., "temp_new_member_alpha", "temp_person_123").
        - If you are *modifying an existing member* or an existing member is part of the output and unchanged, you MUST RETAIN its original "id" (which will be a UUID) from the "Existing Family Tree JSON".
        - If you are *deleting a member*, omit it entirely from the "members" array in your output. Also, ensure any relationships involving that member are removed from the "relationships" array.
    - For "relationships":
        - The "from" and "to" fields MUST refer to either the original "id" of an existing member (UUID) or the temporary string placeholder you assigned to a *newly added* member.
        - For the "id" field of a relationship object itself (e.g., `relationships[0].id`), OMIT this field entirely or set its value to `null`. It will be auto-generated.
    - For ALL OTHER "id" fields within nested objects (e.g., `members[0].conditions[0].id`, `members[0].sources[0].id`), OMIT the "id" field entirely or set its value to `null`, regardless of whether the parent member is new or existing. These IDs will be automatically generated by the system later.

    Schema (this is the target structure for your output):
    {schema_description}

    Existing Family Tree JSON:
    {current_tree_json_string}

    Modification Instructions:
    {modification_prompt_text}

    Based on the "Modification Instructions", modify the "Existing Family Tree JSON" and return the *entire updated* JSON object.
    Ensure all fields specified in the schema are present, using null for optional fields if no information is available, or empty lists [] for list fields.
    Pay close attention to field names, e.g., use "appliesToField" in "sources", not "field".
    When deleting a member, ensure that member is removed from the "members" list and all relationships referencing that member (in "from" or "to") are also removed from the "relationships" list.
    """

    try:
        response = model.generate_content(prompt)
        raw_json_text = response.text
        llm_data = json.loads(raw_json_text) # This is the AI's proposed new state of the tree

        # --- Post-processing for IDs and consistency ---
        member_id_map = {} # Maps IDs used by LLM (temp or existing) to final UUIDs

        processed_members = []
        for member_data in llm_data.get("members", []):
            llm_member_id = member_data.get("id")
            final_member_id = None

            if isinstance(llm_member_id, str) and (llm_member_id.startswith("temp_") or "temp" in llm_member_id.lower()): # Heuristic for temp ID
                final_member_id = str(uuid.uuid4())
                member_id_map[llm_member_id] = final_member_id
            elif isinstance(llm_member_id, str): # Potentially an existing UUID
                try:
                    # Validate if it's a UUID. The LLM was asked to preserve existing valid UUIDs.
                    uuid.UUID(llm_member_id, version=4)
                    final_member_id = llm_member_id
                    member_id_map[llm_member_id] = final_member_id # Map existing UUID to itself
                except ValueError:
                    print(f"Warning: Member ID '{llm_member_id}' from LLM is not a valid UUID nor a recognized temp format. Assigning new UUID.")
                    final_member_id = str(uuid.uuid4())
                    # We need to map the original llm_member_id if relationships might use it
                    member_id_map[llm_member_id] = final_member_id
            else: # ID is missing or not a string
                print(f"Warning: Member data from LLM has missing or invalid 'id': {llm_member_id}. Assigning a new UUID. Data: {member_data}")
                final_member_id = str(uuid.uuid4())
                # If llm_member_id was something, map it so relationships don't break, though it's risky.
                if llm_member_id:
                    member_id_map[str(llm_member_id)] = final_member_id


            member_data["id"] = final_member_id

            # Process nested objects: remove their IDs, handle 'appliesToField'
            for sub_list_key in ["conditions", "allergies", "medications", "vitals", "customTimelineEvents", "sources"]:
                for item in member_data.get(sub_list_key, []):
                    if "id" in item: # LLM should have omitted these.
                        del item["id"]
                    if sub_list_key == "sources" and "field" in item and "appliesToField" not in item:
                         item["appliesToField"] = item.pop("field")
            processed_members.append(member_data)
        llm_data["members"] = processed_members

        # Process relationships: update 'from' and 'to' using member_id_map, remove relationship 'id'
        processed_relationships = []
        valid_final_member_ids = {m["id"] for m in llm_data["members"]} # Set of all member IDs in the processed list

        for rel_data in llm_data.get("relationships", []):
            if "id" in rel_data: # LLM should have omitted this.
                del rel_data["id"]

            original_from_id = rel_data.get("from")
            original_to_id = rel_data.get("to")

            final_from_id = member_id_map.get(original_from_id)
            final_to_id = member_id_map.get(original_to_id)

            if not final_from_id and original_from_id in valid_final_member_ids: # Maybe it was an existing ID not needing mapping
                final_from_id = original_from_id
            if not final_to_id and original_to_id in valid_final_member_ids: # Maybe it was an existing ID not needing mapping
                final_to_id = original_to_id
            
            if final_from_id and final_to_id:
                # Crucially, check if these final IDs actually exist in the processed members list
                if final_from_id in valid_final_member_ids and final_to_id in valid_final_member_ids:
                    rel_data["from"] = final_from_id
                    rel_data["to"] = final_to_id
                    processed_relationships.append(rel_data)
                else:
                    print(f"Warning: Relationship references non-existent member ID after mapping. From: '{original_from_id}'->'{final_from_id}', To: '{original_to_id}'->'{final_to_id}'. Relationship dropped: {rel_data}")
            else:
                print(f"Warning: Could not resolve relationship IDs. From: '{original_from_id}', To: '{original_to_id}'. Relationship dropped: {rel_data}")
        
        llm_data["relationships"] = processed_relationships
        
        # Validate the entire modified structure
        parsed_tree = FamilyTreeData.model_validate(llm_data)
        return parsed_tree

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error (modify_family_tree_data): {e}")
        print(f"Raw text from model: {raw_json_text if 'raw_json_text' in locals() else 'N/A'}")
        # Consider returning the raw text or a more specific error structure
        raise 
    except PydanticValidationError as e:
        print(f"Pydantic Validation Error (modify_family_tree_data): {e.json()}")
        # Propagate the Pydantic error details if possible
        raise 
    except Exception as e:
        print(f"An error occurred during Gemini API call or processing (modify_family_tree_data): {e}")
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        if 'response' in locals() and hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason != 1: # 1 is typically "STOP"
                      print(f"Candidate Finish Reason: {candidate.finish_reason}")
                      print(f"Candidate Safety Ratings: {candidate.safety_ratings if hasattr(candidate, 'safety_ratings') else 'N/A'}")
        raise
