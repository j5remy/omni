from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_notes(text: str, accumulated_notes="") -> str:
    """
    Generates bullet-point notes from input text, considering any existing notes.

    Uses GPT to extract key information while filtering irrelevant content, maintaining
    a natural note-taking style.
    """
    if accumulated_notes.strip():
        user_content = (
            f"Existing notes:\n{accumulated_notes}\n\n"
            f"New text:\n{text}\n\n"
            "Provide bullet point notes of any new important topics or insights that are not already in the existing notes included above."
        )
    else:
        user_content = (
            f"New text:\n{text}\n\n"
            "Provide detailed, organized bullet point notes summarizing the most important topics, key concepts, and insights."
        )

    prompt = [
        {
            "role": "system",
            "content": (
                "You are a highly capable note-taking assistant. Your task is to analyze the provided text and extract only the "
                "most important information and key concepts relative to the context of the text, while completely ignoring any extraneous details such as UI elements, "
                "bookmarks, random numbers, or other irrelevant content. Think of this as if you were the user taking notes for future study. "
                "Remember that you will be taking notes continuously, so do not write anything down that has to do with introductions or conclusions. Keep taking continuous notes. "
                "Your notes should be formatted as clear, descriptive bullet points. Do not group topics together, just take notes as you go as a human would. "
                "Focus on preserving context, highlighting important details, and ensuring that the critical ideas are easy to review."
            )
        },
        {
            "role": "user",
            "content": user_content
        }
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.1, 
        max_tokens=4000,       # lower temperature for more deterministic output        # adjust as needed based on expected output length
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0
    )

    notes = response.choices[0].message.content
    return notes