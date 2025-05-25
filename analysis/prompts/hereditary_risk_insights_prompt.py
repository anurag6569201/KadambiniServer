def get_hereditary_risk_insights_create_prompt(family_json_string):
    prompt = f"""
You are an AI assistant trained to analyze structured family health data and extract generational medical risks.

You will receive a JSON file describing a family, including each member’s medical history and relationships.

Your task is to analyze this JSON and return a valid JSON object with these sections:

1. "highRisks": Conditions that appear multiple times in the family, especially across generations, or have early onset.  
2. "moderateRisks": Conditions found in 1st-degree or 2nd-degree relatives but not consistently or severely.  
3. "lowRisks": Conditions with single or rare occurrence, or those that show weak genetic links.  

Each entry in these categories must include:
- "condition": Name of the medical condition or disorder
- "prevalence": Short explanation of how common it is in the family (e.g., "Multiple occurrences", "Seen in paternal line", "One cousin affected")
- "recommendation": Personalized preventive or screening advice based on that condition

Analyze only what's provided. Do not infer or hallucinate any risks or diagnoses.

Given this family JSON:

<INPUT_JSON_START>
{family_json_string}
<INPUT_JSON_END>

Output only the final JSON in the format below:

<EXAMPLE_OUTPUT_START>
{{
  "highRisks": [
    {{
      "condition": "Type 2 Diabetes",
      "prevalence": "Multiple occurrences in both parental lines",
      "recommendation": "Regular blood glucose monitoring starting by age 30"
    }},
    {{
      "condition": "Cardiovascular Issues",
      "prevalence": "Seen in older generations and male relatives",
      "recommendation": "Adopt a heart-healthy lifestyle and monitor cholesterol annually"
    }}
  ],
  "moderateRisks": [
    {{
      "condition": "Thyroid Disorders",
      "prevalence": "Seen in maternal grandmother and aunt",
      "recommendation": "Periodic thyroid function tests, especially after age 30"
    }}
  ],
  "lowRisks": [
    {{
      "condition": "Colon Cancer",
      "prevalence": "Single occurrence in an uncle",
      "recommendation": "Standard screening beginning at recommended age"
    }}
  ]
}}
<EXAMPLE_OUTPUT_END>

Return only valid JSON in this format — no extra explanation or headings outside the JSON object. The output must be parsable by json.loads().
"""
    return prompt
