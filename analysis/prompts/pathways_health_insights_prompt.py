def pathways_health_insights_prompt(family_json_string):
    prompt = f"""
You are an AI trained to generate **personalized Smart Health Pathways** for individuals based on their family health data.

You will receive a JSON structure that includes medical conditions, medications, vitals, lifestyle choices, allergies, and other timeline events for each member of a family.

Your task is to:
- Generate 2 personalized, actionable recommendations (called "Smart Health Pathways") for each individual.
- Focus on managing existing conditions, preventive strategies based on lifestyle or vitals, and any medication/lab/imaging follow-up.
- Use concrete, medically appropriate suggestions (e.g., "Continue managing Type 2 Diabetes with diet and medication", "Ensure allergy is documented", "Schedule thyroid check every 6 months", "Balance sedentary lifestyle with walking 30 min/day").

**Important constraints**:
- Use only the information present in the input data. Do not invent conditions or recommendations.
- Be brief and focused — each recommendation should be a single sentence.
- Do not include condition definitions or general health advice unless it's directly related to the individual's context.

Here is the input data:

<INPUT_JSON_START>
{family_json_string}
<INPUT_JSON_END>

Return ONLY a valid JSON object in this format:

<EXAMPLE_OUTPUT_START>
{{
  "f5cdf5c3-c593-46dc-8f71-18cba8598dc2": [
    "Continue managing Type 2 Diabetes with diet and medication.",
    "Monitor blood pressure regularly."
  ],
  "c9027569-d053-4da0-9408-63f8743a184a": [
    "Maintain Eltroxin dosage for Hypothyroidism.",
    "Consider regular checks for B12 and iron levels."
  ],
  "7608d7cf-4a28-454e-bbfe-67b730db76fe": [
    "Ensure Penicillin allergy is clearly documented with all healthcare providers.",
    "Balance sedentary work with regular physical activity."
  ]
}}
<EXAMPLE_OUTPUT_END>

Return only this JSON object — no headings or other text. It must be parsable using `json.loads()`.
"""
    return prompt
