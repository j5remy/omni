from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def format_notes(accumulated_notes: str) -> str:
    """
    Formats raw bullet point notes into a structured, readable format by grouping
    related points and adding appropriate headings.
    """
    system_prompt = (
        "You are a note formatting assistant. Your task is to take raw, sequential bullet point notes and organize them "
        "into a final, well-structured format that is easy for a human to read. Group related bullet points into subtopics or "
        "categories when the information is related, and add appropriate headings if needed. If no grouping is necessary, simply "
        "format the notes nicely. Do not add new information—only re-organize and format what is provided. Do not shorten the information at all."
    )
    
    user_prompt = (
        f"Here are the raw notes:\n\n{accumulated_notes}\n\n"
        "Please reformat these notes into a final version with clear headings and grouped bullet points where appropriate. "
        "Ensure the output is clean and organized."
    )
    
    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.1, 
        max_tokens=4000, 
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0
    )
    
    final_notes = response.choices[0].message.content.strip()
    return final_notes
