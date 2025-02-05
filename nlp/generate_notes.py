from openai import OpenAI

# Make sure to set your API key
api_key = "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"
client = OpenAI(api_key=api_key)

def generate_notes(text):
    prompt = [
        {
            "role": "system",
            "content": (
                "You are a highly capable note-taking assistant. Your task is to analyze the provided text and extract only the "
                "most important information and key concepts relative to the context of the text, while completely ignoring any extraneous details such as UI elements, "
                "bookmarks, random numbers, or other irrelevant content. Think of this as if you were the user taking notes for future study. "
                "Remember that you will be taking notes continuously, so do not write anything down that has to do with introductions or conclusions. Keep taking continuous notes."
                "Your notes should be formatted as clear, concise bullet points. If there are multiple topics or sections, group related points together "
                "using sub-bullets where appropriate. Focus on preserving context, highlighting important details, and ensuring that the critical ideas are easy to review."
            )
        },
        {
            "role": "user",
            "content": f"Please analyze the following text and provide detailed, organized bullet point notes summarizing the most important topics, key concepts, and insights:\n\n{text}"
        }
    ]   

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.1
    )

    notes = response.choices[0].message.content
    return notes