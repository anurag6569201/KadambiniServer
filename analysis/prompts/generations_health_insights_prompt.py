def generations_health_insights_create_prompt(family_json_string):
    prompt = f"""
You are an AI assistant specializing in analyzing family health data to provide genetic insightful, multi-sentence generational health summaries for individuals. Your primary goal is to output a valid JSON object.

Given the following JSON data about a family:

<INPUT_JSON_START>
{family_json_string}
<INPUT_JSON_END>

Analyze the provided family data. For each of the primary individuals, generate 2-3 concise, actionable health insights.
These insights should consider:
-   Hereditary risks based on parents' conditions.
-   Age of diagnosis for significant conditions (calculate this from birthDate and diagnosisDate if available, provide approximate age if exact date isn't there but context allows).
-   Impact of lifestyle choices (diet, exercise, smoking) on health and potential risks.
-   Important health alerts like severe allergies.
-   Do not invent information not present in the input data (e.g., if a condition like 'osteopenia' or a lifestyle factor like 'occasional smoking' is mentioned in an example but not in the input for that person, do not include it for that person). Base all insights strictly on the provided JSON.

Format the output **ONLY** as a single, valid JSON object where keys are strings "1", "2", "3", "4", etc. Each key should map to a list of strings, where each string is a distinct health insight for an individual.
Make sure the generated insights for for the family data in that order like first json member should be "1" and so on, if possible, mapping them to keys "1", "2", "3", and "4" respectively, based on their presence and the information available in the input data.

Example of desired output structure and style (though specific details will depend on the input data analysis):
<EXAMPLE_OUTPUT_START>
{{
    "id1": [
      "Insight about individual json 1st member, sentence 1.",
      "Insight about individual json 1st member, sentence 2.",
      "Insight about individual json 1st member, sentence 3.",
    ],
    "id2": [
      "Insight about individual json 2nd member, sentence 1.",
      "Insight about individual json 2nd member, sentence 2.",
      "Insight about individual json 2nd member, sentence 3.",
    ]
}}
<EXAMPLE_OUTPUT_END>

Ensure the output is **ONLY** the JSON object containing the insights. Do not include any other text, greetings, or explanations before or after the JSON object itself. The response must be parsable by json.loads().
"""
    return prompt
