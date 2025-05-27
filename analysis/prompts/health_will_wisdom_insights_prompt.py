def health_will_and_wisdom_prompt(family_json_string):
    prompt = f"""
You are an AI health advisor tasked with writing a "Health Will & Wisdom" — a reflective legacy of health insights distilled from a family’s medical history, lifestyles, and health journeys across generations.

You will be given structured JSON data containing detailed family member information: conditions, medications, lifestyle choices, allergies, timeline events, and relationships.

From this, extract cross-generational lessons, patterns, and actionable wisdom. Focus on insights that reflect:
- Hereditary condition patterns (e.g., diabetes, heart issues).
- Lifestyle influences (diet, exercise, stress, work-life balance).
- Notable events (e.g., allergies, late diagnoses, health improvements).
- Preventive strategies that future generations can follow.

**Your Output Format**:
Return a JSON array of objects, each with a `title` and a `description`. The tone should be warm, legacy-style, insightful, and based strictly on the data — not generic.

Each object should follow this structure:

```json
[
  {{
    "title": "Proactive Monitoring Matters",
    "description": "Regular screening from age 40 onwards could help detect pre-diabetic conditions early, as seen with diabetes onset in the 50s for Rajesh and Sunita."
  }},
  {{
    "title": "Diet Choices, Lifelong Impact",
    "description": "Meera's anemia underscores nutritional awareness, especially for vegetarian diets. Iron-rich foods and supplements are key."
  }}
]
Important:

Use real names and data from the input JSON where applicable.

Do not invent data not present.

Output must be a valid JSON array and parsable by json.loads().

Do not include any explanations, greetings, or markdown — just the JSON.

Here is the input family data:

<INPUT_JSON_START>
{family_json_string}
<INPUT_JSON_END>
"""
    
    return prompt